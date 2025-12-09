# Code Interview Platform - Project Structure

This repository contains a full-stack collaborative coding interview platform.

## Project Structure

```
codespaces-react/
├── client/                    # Frontend React application (to be moved)
│   ├── src/                   # React components and pages
│   ├── public/                # Static assets
│   ├── package.json           # Frontend dependencies
│   └── vite.config.js         # Vite configuration
│
├── server/                    # Backend Node.js API server
│   ├── openapi.yaml           # Complete API specification
│   ├── WEBSOCKET_PROTOCOL.md  # WebSocket protocol docs
│   ├── README.md              # Server documentation
│   └── src/                   # Server source code (to be implemented)
│
├── docs/                      # Additional documentation
├── .devcontainer/             # Dev container configuration
└── README.md                  # This file
```

## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+ (for backend)
- Redis 6+ (for backend)
- Docker (for code execution)

### Running the Frontend Only

The frontend currently works standalone with peer-to-peer WebRTC:

```bash
# From root directory
cd client
npm install
npm start
```

Visit `http://localhost:3000` to use the app.

### Running Full Stack (Backend + Frontend)

1. **Start Backend:**
```bash
cd server
npm install
npm run dev
```

2. **Start Frontend:**
```bash
cd client
npm install
npm start
```

3. **Access the application:**
   - Frontend: `http://localhost:3001`
   - Backend API: `http://localhost:3000/api`
   - API Docs: `http://localhost:3000/api-docs`

## Migration Status

### ✅ Completed
- Frontend application fully functional
- OpenAPI specification created
- WebSocket protocol documented
- Database schema designed
- Architecture documentation

### ⏳ Pending
- Move frontend files to `client/` directory
- Initialize backend Node.js project
- Implement REST API endpoints
- Implement WebSocket server
- Set up database and migrations
- Implement code execution service
- Update frontend to use backend APIs

## Features

### Current (Frontend Only)
- ✅ Create and share interview session links
- ✅ Real-time collaborative code editing (P2P via WebRTC)
- ✅ Syntax highlighting for JavaScript, Python, Java, C++
- ✅ JavaScript code execution in browser

### Planned (With Backend)
- ⏳ Centralized session management
- ⏳ Session persistence and history
- ⏳ Server-side code execution for all languages
- ⏳ User authentication (optional)
- ⏳ Session recording and playback
- ⏳ Advanced collaboration features

## Architecture

### Current Architecture (P2P)
```
┌─────────┐     WebRTC      ┌─────────┐
│ Client  │◄───────────────►│ Client  │
│    A    │   (P2P Sync)    │    B    │
└─────────┘                 └─────────┘
     │                           │
     └────────►Signaling◄────────┘
              Server
        (signaling.yjs.dev)
```

### Future Architecture (Client-Server)
```
┌─────────┐                 ┌─────────┐
│ Client  │    WebSocket    │ Backend │
│    A    │◄───────────────►│ Server  │
└─────────┘                 └────┬────┘
                                 │
┌─────────┐    WebSocket    ┌────┴────┐
│ Client  │◄───────────────►│Database │
│    B    │                 └─────────┘
└─────────┘
```

## Technology Stack

### Frontend
- React 18
- CodeMirror 6
- Y.js (CRDT)
- React Router
- Vite

### Backend (Planned)
- Node.js + Express
- PostgreSQL
- Redis
- Y.js + WebSocket
- Docker (for code execution)

## API Documentation

Complete API documentation is available in:
- **OpenAPI Spec:** `server/openapi.yaml`
- **WebSocket Protocol:** `server/WEBSOCKET_PROTOCOL.md`
- **Server README:** `server/README.md`

You can view the API spec using:
- [Swagger Editor](https://editor.swagger.io/) (paste the YAML)
- [Redoc](https://github.com/Redocly/redoc)
- [Stoplight Studio](https://stoplight.io/studio)

## Development Workflow

### Phase 1: Restructure (Current)
1. Move frontend files to `client/` directory
2. Keep frontend working independently
3. Set up backend project structure

### Phase 2: Backend Implementation
1. Initialize Node.js project in `server/`
2. Implement REST API endpoints
3. Set up PostgreSQL and Redis
4. Implement WebSocket server
5. Add code execution service

### Phase 3: Integration
1. Update frontend to use backend APIs
2. Replace WebRTC with WebSocket
3. Add authentication (optional)
4. Deploy both services

## Contributing

See individual README files in `client/` and `server/` directories for specific contribution guidelines.

## License

MIT

---

## Next Steps

To complete the migration, run:

```bash
# Move frontend files to client directory
bash move-to-client.sh

# Or manually:
mv src client/
mv public client/
mv index.html client/
mv vite.config.js client/
mv jsconfig.json client/
mv package.json client/
mv package-lock.json client/
mv node_modules client/
```

Then start implementing the backend according to `server/README.md`.
