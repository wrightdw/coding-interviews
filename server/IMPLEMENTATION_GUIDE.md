# Backend Implementation Guide

This guide provides step-by-step instructions for implementing the backend server based on the OpenAPI specification.

## Phase 1: Project Setup

### 1.1 Initialize Node.js Project

```bash
cd server
npm init -y
```

### 1.2 Install Core Dependencies

```bash
# Web framework
npm install express cors helmet

# WebSocket
npm install ws y-websocket yjs

# Database
npm install pg redis

# Validation & utilities
npm install joi uuid

# Security & middleware
npm install express-rate-limit

# Logging
npm install winston

# Environment variables
npm install dotenv

# Development dependencies
npm install --save-dev nodemon
```

### 1.3 Install Code Execution Dependencies

```bash
# Docker integration
npm install dockerode

# Alternative: VM2 for JavaScript only
npm install vm2
```

### 1.4 Optional: TypeScript Setup

```bash
npm install --save-dev typescript @types/node @types/express @types/ws
npx tsc --init
```

## Phase 2: Database Setup

### 2.1 Create PostgreSQL Database

```bash
createdb codeinterview
```

### 2.2 Create Migration Files

Create `server/migrations/001_initial_schema.sql`:

```sql
-- Sessions table
CREATE TABLE sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255),
  language VARCHAR(20) NOT NULL DEFAULT 'javascript',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL,
  active_participants INTEGER DEFAULT 0,
  code_content TEXT,
  yjs_state BYTEA
);

CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- Code snapshots table
CREATE TABLE code_snapshots (
  snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
  code_content TEXT NOT NULL,
  language VARCHAR(20) NOT NULL,
  saved_at TIMESTAMP NOT NULL DEFAULT NOW(),
  user_id VARCHAR(255)
);

CREATE INDEX idx_snapshots_session ON code_snapshots(session_id);

-- History entries table
CREATE TABLE history_entries (
  entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  user_id VARCHAR(255),
  change_type VARCHAR(50) NOT NULL,
  description TEXT,
  code_snapshot TEXT
);

CREATE INDEX idx_history_session ON history_entries(session_id, timestamp);
```

### 2.3 Run Migrations

```bash
psql codeinterview < migrations/001_initial_schema.sql
```

## Phase 3: Core Implementation

### 3.1 Create Entry Point (`src/index.js`)

```javascript
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { createServer } = require('http');
const { setupWebSocket } = require('./websocket/server');
const routes = require('./routes');
const { errorHandler } = require('./middleware/errorHandler');
const logger = require('./config/logger');

const app = express();
const server = createServer(app);
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors({ origin: process.env.CORS_ORIGIN }));
app.use(express.json());

// Routes
app.use('/api', routes);

// Error handling
app.use(errorHandler);

// WebSocket setup
setupWebSocket(server);

// Start server
server.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
});

module.exports = { app, server };
```

### 3.2 Session Service (`src/services/sessionService.js`)

```javascript
const { v4: uuidv4 } = require('uuid');
const pool = require('../config/database');

class SessionService {
  async createSession({ language = 'javascript', title = null, expiresIn = 24 }) {
    const sessionId = uuidv4();
    const expiresAt = new Date(Date.now() + expiresIn * 60 * 60 * 1000);
    
    const query = `
      INSERT INTO sessions (session_id, title, language, expires_at)
      VALUES ($1, $2, $3, $4)
      RETURNING *
    `;
    
    const result = await pool.query(query, [sessionId, title, language, expiresAt]);
    return result.rows[0];
  }

  async getSession(sessionId) {
    const query = 'SELECT * FROM sessions WHERE session_id = $1';
    const result = await pool.query(query, [sessionId]);
    
    if (result.rows.length === 0) {
      throw new Error('SESSION_NOT_FOUND');
    }
    
    return result.rows[0];
  }

  async updateSession(sessionId, updates) {
    const fields = [];
    const values = [];
    let paramIndex = 1;

    Object.entries(updates).forEach(([key, value]) => {
      fields.push(`${key} = $${paramIndex}`);
      values.push(value);
      paramIndex++;
    });

    values.push(sessionId);
    
    const query = `
      UPDATE sessions 
      SET ${fields.join(', ')}
      WHERE session_id = $${paramIndex}
      RETURNING *
    `;
    
    const result = await pool.query(query, values);
    
    if (result.rows.length === 0) {
      throw new Error('SESSION_NOT_FOUND');
    }
    
    return result.rows[0];
  }

  async deleteSession(sessionId) {
    const query = 'DELETE FROM sessions WHERE session_id = $1';
    const result = await pool.query(query, [sessionId]);
    
    if (result.rowCount === 0) {
      throw new Error('SESSION_NOT_FOUND');
    }
  }

  async saveCodeSnapshot(sessionId, code, language, userId) {
    const query = `
      INSERT INTO code_snapshots (session_id, code_content, language, user_id)
      VALUES ($1, $2, $3, $4)
      RETURNING snapshot_id, saved_at
    `;
    
    const result = await pool.query(query, [sessionId, code, language, userId]);
    return result.rows[0];
  }

  async getCode(sessionId) {
    const query = 'SELECT code_content, language FROM sessions WHERE session_id = $1';
    const result = await pool.query(query, [sessionId]);
    
    if (result.rows.length === 0) {
      throw new Error('SESSION_NOT_FOUND');
    }
    
    return result.rows[0];
  }
}

module.exports = new SessionService();
```

### 3.3 Code Execution Service (`src/services/executionService.js`)

```javascript
const Docker = require('dockerode');
const docker = new Docker();

class ExecutionService {
  async executeCode({ code, language, stdin = '', timeout = 5000 }) {
    const startTime = Date.now();
    
    try {
      const result = await this.runInDocker({
        code,
        language,
        stdin,
        timeout
      });
      
      const executionTime = Date.now() - startTime;
      
      return {
        success: result.exitCode === 0,
        stdout: result.stdout,
        stderr: result.stderr,
        exitCode: result.exitCode,
        executionTime,
        error: result.error
      };
    } catch (error) {
      return {
        success: false,
        stdout: '',
        stderr: '',
        exitCode: -1,
        executionTime: Date.now() - startTime,
        error: error.message
      };
    }
  }

  async runInDocker({ code, language, stdin, timeout }) {
    const config = this.getLanguageConfig(language);
    
    // Create container
    const container = await docker.createContainer({
      Image: config.image,
      Cmd: config.getCommand(code),
      Memory: 256 * 1024 * 1024, // 256MB
      NetworkDisabled: true,
      AttachStdout: true,
      AttachStderr: true
    });

    // Start container
    await container.start();

    // Set timeout
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('EXECUTION_TIMEOUT')), timeout);
    });

    try {
      // Wait for container with timeout
      const result = await Promise.race([
        container.wait(),
        timeoutPromise
      ]);

      // Get logs
      const logs = await container.logs({
        stdout: true,
        stderr: true
      });

      await container.remove();

      return {
        exitCode: result.StatusCode,
        stdout: logs.toString(),
        stderr: '',
        error: null
      };
    } catch (error) {
      await container.remove({ force: true });
      throw error;
    }
  }

  getLanguageConfig(language) {
    const configs = {
      javascript: {
        image: 'node:18-alpine',
        getCommand: (code) => ['node', '-e', code]
      },
      python: {
        image: 'python:3.11-alpine',
        getCommand: (code) => ['python', '-c', code]
      },
      java: {
        image: 'openjdk:17-alpine',
        getCommand: (code) => {
          // Java requires file compilation
          return ['sh', '-c', `echo '${code}' > Main.java && javac Main.java && java Main`]
        }
      },
      cpp: {
        image: 'gcc:latest',
        getCommand: (code) => {
          return ['sh', '-c', `echo '${code}' > main.cpp && g++ main.cpp -o main && ./main`]
        }
      }
    };

    return configs[language] || configs.javascript;
  }
}

module.exports = new ExecutionService();
```

### 3.4 WebSocket Server (`src/websocket/server.js`)

```javascript
const WebSocket = require('ws');
const Y = require('yjs');
const { setupWSConnection } = require('y-websocket/bin/utils');
const sessionService = require('../services/sessionService');
const logger = require('../config/logger');

const sessions = new Map(); // sessionId -> { doc, connections }

function setupWebSocket(server) {
  const wss = new WebSocket.Server({ 
    server,
    path: '/ws'
  });

  wss.on('connection', async (ws, req) => {
    const urlParts = req.url.split('/');
    const sessionId = urlParts[urlParts.length - 1];

    logger.info(`WebSocket connection attempt for session: ${sessionId}`);

    try {
      // Verify session exists
      await sessionService.getSession(sessionId);

      // Get or create Y.js document for session
      if (!sessions.has(sessionId)) {
        const ydoc = new Y.Doc();
        sessions.set(sessionId, {
          doc: ydoc,
          connections: new Set()
        });
      }

      const session = sessions.get(sessionId);
      session.connections.add(ws);

      // Set up Y.js WebSocket connection
      setupWSConnection(ws, req, {
        gc: true
      });

      // Update participant count
      await sessionService.updateSession(sessionId, {
        active_participants: session.connections.size
      });

      // Handle disconnect
      ws.on('close', async () => {
        session.connections.delete(ws);
        
        if (session.connections.size === 0) {
          // Clean up empty sessions after delay
          setTimeout(() => {
            if (session.connections.size === 0) {
              sessions.delete(sessionId);
              logger.info(`Cleaned up empty session: ${sessionId}`);
            }
          }, 60000); // 1 minute
        }

        await sessionService.updateSession(sessionId, {
          active_participants: session.connections.size
        });

        logger.info(`Client disconnected from session: ${sessionId}`);
      });

      logger.info(`Client connected to session: ${sessionId}`);
    } catch (error) {
      logger.error(`WebSocket connection error: ${error.message}`);
      ws.close(1008, 'Session not found');
    }
  });

  return wss;
}

module.exports = { setupWebSocket };
```

### 3.5 Routes (`src/routes/index.js`)

```javascript
const express = require('express');
const router = express.Router();
const sessionController = require('../controllers/sessionController');
const executeController = require('../controllers/executeController');
const { validateSession, validateExecution } = require('../middleware/validation');
const rateLimit = require('express-rate-limit');

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

router.use(limiter);

// Session routes
router.post('/sessions', validateSession, sessionController.createSession);
router.get('/sessions/:sessionId', sessionController.getSession);
router.patch('/sessions/:sessionId', validateSession, sessionController.updateSession);
router.delete('/sessions/:sessionId', sessionController.deleteSession);
router.get('/sessions/:sessionId/code', sessionController.getCode);
router.post('/sessions/:sessionId/code', sessionController.saveCode);

// Execution route
router.post('/execute', validateExecution, executeController.executeCode);

module.exports = router;
```

## Phase 4: Testing

### 4.1 Create Test Files

```bash
npm install --save-dev jest supertest
```

### 4.2 Example Test (`tests/sessions.test.js`)

```javascript
const request = require('supertest');
const { app } = require('../src/index');

describe('Session API', () => {
  let sessionId;

  test('POST /api/sessions - create session', async () => {
    const response = await request(app)
      .post('/api/sessions')
      .send({ language: 'javascript' });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('sessionId');
    sessionId = response.body.sessionId;
  });

  test('GET /api/sessions/:id - get session', async () => {
    const response = await request(app)
      .get(`/api/sessions/${sessionId}`);

    expect(response.status).toBe(200);
    expect(response.body.sessionId).toBe(sessionId);
  });
});
```

## Phase 5: Deployment

### 5.1 Create Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "src/index.js"]
```

### 5.2 Create docker-compose.yml

```yaml
version: '3.8'

services:
  server:
    build: ./server
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/codeinterview
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: codeinterview
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  client:
    build: ./client
    ports:
      - "3001:80"
    depends_on:
      - server

volumes:
  postgres_data:
  redis_data:
```

## Summary

This guide provides the complete implementation path for the backend. Follow each phase sequentially:

1. ✅ Set up project structure
2. ✅ Install dependencies
3. ✅ Configure database
4. ✅ Implement core services
5. ✅ Create API routes
6. ✅ Set up WebSocket server
7. ✅ Add tests
8. ✅ Deploy

Refer to `openapi.yaml` for complete API specifications and `WEBSOCKET_PROTOCOL.md` for WebSocket details.
