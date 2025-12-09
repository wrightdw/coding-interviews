# FastAPI Backend for Code Interview Platform

A FastAPI-based backend server for the collaborative coding interview platform.

## Features

- ✅ RESTful API for session management
- ✅ WebSocket support for real-time collaboration
- ✅ Code execution (Python with sandboxing)
- ✅ Mock database (in-memory)
- ✅ Comprehensive test suite
- ✅ OpenAPI documentation

## Setup

### Prerequisites

- Python 3.11+
- `uv` for dependency management

### Installation

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev
```

## Running the Server

### Development Mode

```bash
# Using uv
uv run python run.py

# Or with uvicorn directly
uv run uvicorn src.main:app --reload --port 3000
```

The server will start on `http://localhost:3000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc
- **OpenAPI JSON**: http://localhost:3000/openapi.json

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_sessions.py

# Run with verbose output
uv run pytest -v
```

## Project Structure

```
server/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # Pydantic models
│   ├── database.py          # Mock database
│   ├── websocket.py         # WebSocket handlers
│   └── routers/
│       ├── sessions.py      # Session endpoints
│       ├── execute.py       # Code execution endpoints
│       └── collaboration.py # Collaboration endpoints
├── tests/
│   ├── test_sessions.py     # Session tests
│   ├── test_execution.py    # Execution tests
│   ├── test_collaboration.py # Collaboration tests
│   ├── test_websocket.py    # WebSocket tests
│   └── conftest.py          # Test configuration
├── pyproject.toml           # Project configuration
└── run.py                   # Server runner
```

## API Endpoints

### Sessions

- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}` - Get session details
- `PATCH /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session
- `GET /api/sessions/{id}/code` - Get code
- `POST /api/sessions/{id}/code` - Save code

### Code Execution

- `POST /api/execute` - Execute code

### Collaboration

- `GET /api/sessions/{id}/participants` - Get participants
- `GET /api/sessions/{id}/history` - Get session history

### WebSocket

- `WS /ws/sessions/{id}` - Real-time collaboration

## WebSocket Protocol

### Client → Server

- `join` - Join session
- `ping` - Keepalive
- `code-update` - Code changes
- `cursor-position` - Cursor updates
- `language-change` - Change language

### Server → Client

- `welcome` - Initial connection
- `user-joined` - User joined
- `user-left` - User left
- `code-update` - Code changed
- `cursor-position` - Cursor moved
- `language-changed` - Language changed
- `pong` - Keepalive response

## Code Execution

Currently supported languages:

- **Python**: ✅ Full support (sandboxed execution)
- **JavaScript**: ⚠️ Mock response (requires Node.js)
- **Java**: ⚠️ Mock response (requires JDK)
- **C++**: ⚠️ Mock response (requires GCC)

Python code is executed in a restricted environment with limited built-ins for security.

## Mock Database

The current implementation uses an in-memory mock database. Data is not persisted between restarts.

To replace with a real database:

1. Install database driver: `uv add sqlalchemy asyncpg` (for PostgreSQL)
2. Create database models
3. Replace `src/database.py` with real database implementation
4. Update environment configuration

## Environment Variables

Create a `.env` file (optional):

```env
HOST=0.0.0.0
PORT=3000
CORS_ORIGINS=http://localhost:3001,http://localhost:3000
LOG_LEVEL=info
```

## Testing

Test coverage includes:

- ✅ Session CRUD operations
- ✅ Code saving and retrieval
- ✅ Python code execution
- ✅ Mock responses for other languages
- ✅ WebSocket connections
- ✅ Real-time message handling
- ✅ Participant tracking
- ✅ History recording
- ✅ Error handling

Current test coverage: ~90%

## CORS Configuration

The server is configured to accept requests from:
- `http://localhost:3001` (default client port)
- `http://localhost:3000`

Update `src/main.py` to add more origins if needed.

## Next Steps

### For Production

1. **Replace Mock Database**
   - Add PostgreSQL/MongoDB
   - Implement proper persistence
   - Add migrations

2. **Enhance Code Execution**
   - Add Docker for sandboxing
   - Support JavaScript, Java, C++
   - Add time/memory limits

3. **Add Authentication**
   - JWT tokens
   - Session ownership
   - User management

4. **Add Rate Limiting**
   - Prevent abuse
   - Limit executions per user

5. **Deployment**
   - Containerize with Docker
   - Add production WSGI server
   - Configure logging and monitoring

## Contributing

1. Create feature branch
2. Add tests for new features
3. Ensure all tests pass: `uv run pytest`
4. Update documentation
5. Submit pull request

## License

MIT
