# Coding Interview Platform - Backend

FastAPI backend server for the collaborative coding interview platform.

## Overview

This backend provides:
- REST API for session management, code storage, and execution
- WebSocket server for real-time collaboration
- Mock database (in-memory storage)
- Python code execution with sandboxing
- Comprehensive test suite with integration tests

## Architecture

- **Framework**: FastAPI 0.115+
- **Package Manager**: uv (modern Python package management)
- **Database**: Mock in-memory storage (to be replaced with real database)
- **WebSocket**: Real-time bidirectional communication
- **Testing**: pytest with async support

## Project Structure

```
server/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Pydantic models (9 models)
│   ├── database.py          # Mock database
│   ├── websocket.py         # WebSocket connection manager
│   └── routers/
│       ├── sessions.py      # Session endpoints
│       ├── collaboration.py # Collaboration endpoints
│       └── execute.py       # Code execution endpoint
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_main.py         # Main app tests (4 tests)
│   ├── test_sessions.py     # Session tests (10 tests)
│   ├── test_execution.py    # Execution tests (9 tests)
│   ├── test_collaboration.py # Collaboration tests (7 tests)
│   ├── test_websocket.py    # WebSocket tests (7 tests)
│   └── test_integration.py  # Integration tests (13 tests)
├── pyproject.toml           # Dependencies and config
├── run.py                   # Server runner script
├── setup_and_test.sh        # Automated setup script
└── README.md               # This file
```

## API Endpoints

### REST Endpoints

- `POST /api/sessions` - Create new interview session
- `GET /api/sessions/{sessionId}` - Get session details
- `PATCH /api/sessions/{sessionId}` - Update session
- `DELETE /api/sessions/{sessionId}` - Delete session
- `GET /api/sessions/{sessionId}/code` - Get saved code
- `POST /api/sessions/{sessionId}/code` - Save code
- `POST /api/execute` - Execute code
- `GET /api/sessions/{sessionId}/participants` - Get participants
- `GET /api/sessions/{sessionId}/history` - Get session history
- `GET /health` - Health check

### WebSocket Endpoint

- `WS /ws/sessions/{sessionId}` - Real-time collaboration

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- Node.js 18+ (for frontend)

### Installation & Setup

```bash
# 1. Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Navigate to server directory
cd server

# 3. Install dependencies
uv sync

# 4. Run tests to verify installation
uv run pytest -v

# 5. Start the backend server
uv run python run.py
```

The server will start on `http://localhost:3000`

### Running the Frontend

```bash
# In a separate terminal, navigate to client directory
cd client

# Install dependencies (if not already done)
npm install

# Start the development server
npm start
```

The frontend will start on `http://localhost:3001`

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test suites
uv run pytest tests/test_sessions.py      # Session tests
uv run pytest tests/test_execution.py     # Execution tests
uv run pytest tests/test_collaboration.py # Collaboration tests
uv run pytest tests/test_websocket.py     # WebSocket tests
uv run pytest tests/test_integration.py   # Integration tests

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run only integration tests
uv run pytest tests/test_integration.py -v

# Run tests matching a pattern
uv run pytest -k "workflow"

# Run tests and see print statements
uv run pytest -v -s
```

### Test Suite Overview

The test suite includes:
- **Unit tests**: Test individual endpoints and functions (28 tests)
- **Integration tests**: Test complete client-server workflows (13 tests)
- **WebSocket tests**: Test real-time communication (7 tests)
- **Total**: 48 test cases covering all functionality

### Integration Tests

Integration tests verify complete workflows:
- ✅ Complete interview session lifecycle
- ✅ Multi-user collaboration
- ✅ Language switching
- ✅ Code execution feedback loop
- ✅ Session persistence across reconnects
- ✅ Concurrent code updates
- ✅ Participant tracking
- ✅ Cursor synchronization
- ✅ Error recovery
- ✅ Full interview simulation
- ✅ Edge cases (empty code, long code, rapid creation)

## Development

### Starting the Server

```bash
# Development mode (with auto-reload)
uv run python run.py

# Production mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 3000

# Custom port
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Environment Configuration

The server runs on port 3000 by default. CORS is configured to allow requests from:
- `http://localhost:3001` (frontend dev server)
- `http://localhost:3000` (same origin)

### Development Workflow

```bash
# 1. Make code changes
# 2. Run tests
uv run pytest -v

# 3. Run integration tests
uv run pytest tests/test_integration.py -v

# 4. Start server (auto-reload enabled)
uv run python run.py

# 5. Test with frontend
cd ../client && npm start
```

## Complete Testing Workflow

### Automated Setup and Test

```bash
# Run the automated setup and test script
cd server
chmod +x setup_and_test.sh
./setup_and_test.sh
```

This script will:
1. Install dependencies with uv
2. Run all tests
3. Display results

### Manual Full-Stack Testing

```bash
# Terminal 1: Backend
cd server
uv sync
uv run pytest -v          # Run all tests
uv run python run.py      # Start backend

# Terminal 2: Frontend
cd client
npm install
npm start                 # Start frontend

# Terminal 3: Run integration tests
cd server
uv run pytest tests/test_integration.py -v

# Open browser to http://localhost:3001
# Create a session and test real-time collaboration
```

## API Usage Examples

### Create Session

```bash
curl -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "title": "Test Interview"}'
```

### Save Code

```bash
curl -X POST http://localhost:3000/api/sessions/{sessionId}/code \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello\")", "language": "python"}'
```

### Execute Code

```bash
curl -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(2+2)", "language": "python", "timeout": 5}'
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:3000/ws/sessions/{sessionId}');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.send(JSON.stringify({
  type: 'join',
  userId: 'user-123',
  data: { name: 'John Doe' }
}));
```

## Running Commands Summary

### Backend Commands

```bash
# Setup
cd server
uv sync                                      # Install dependencies

# Testing
uv run pytest                                # Run all tests
uv run pytest -v                             # Verbose output
uv run pytest tests/test_integration.py      # Integration tests only
uv run pytest --cov=src                      # With coverage
uv run pytest -k "workflow"                  # Pattern matching

# Running
uv run python run.py                         # Start server (dev mode)
uv run uvicorn src.main:app --reload         # Alternative start
```

### Frontend Commands

```bash
# Setup
cd client
npm install                                  # Install dependencies

# Running
npm start                                    # Start dev server
npm run build                                # Build for production
npm test                                     # Run tests
```

### Full Application Commands

```bash
# From project root
cd server && uv run python run.py &          # Start backend in background
cd client && npm start                       # Start frontend

# Or use two terminals
# Terminal 1: cd server && uv run python run.py
# Terminal 2: cd client && npm start
```

```

## Troubleshooting

### Tests Failing

```bash
# Clear any cached files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name ".pytest_cache" -exec rm -r {} +

# Reinstall dependencies
uv sync --reinstall

# Run tests again
uv run pytest -v
```

### Server Won't Start

```bash
# Check if port 3000 is already in use
lsof -i :3000

# Kill existing process
kill -9 <PID>

# Or use a different port
uv run uvicorn src.main:app --port 8000
```

### WebSocket Connection Issues

- Ensure backend is running on port 3000
- Check CORS settings in `src/main.py`
- Verify WebSocket URL format: `ws://localhost:3000/ws/sessions/{sessionId}`
- Check browser console for connection errors

### Frontend Won't Connect to Backend

```bash
# Check backend is running
curl http://localhost:3000/health

# Check CORS configuration in server/src/main.py
# Should include: http://localhost:3001

# Verify frontend API URL (should be http://localhost:3000)
```

## Performance

- Code execution timeout: 5 seconds (configurable, max 10s)
- WebSocket ping interval: 30 seconds
- Max concurrent connections: Unlimited (resource-dependent)
- Session expiry: 24 hours (configurable)

## Security Notes

**Current Implementation (Development)**:
- ⚠️ No authentication/authorization
- ⚠️ Code execution uses subprocess with timeout
- ⚠️ No rate limiting
- ⚠️ CORS allows all origins from localhost

**Production Requirements**:
- ✅ Add JWT authentication
- ✅ Implement proper code sandboxing (containers/VMs)
- ✅ Add rate limiting
- ✅ Restrict CORS to specific domains
- ✅ Enable HTTPS/WSS
- ✅ Add input validation and sanitization
- ✅ Implement user quotas

## Next Steps

1. Replace mock database with PostgreSQL/MongoDB
2. Add authentication and authorization
3. Implement Y.js CRDT for conflict-free collaboration
4. Add rate limiting and security measures
5. Deploy to production environment
6. Add Redis for session management
7. Implement code execution in isolated containers
8. Add user management and quotas
9. Implement session recording and playback
10. Add code review and feedback features

## Documentation

- [OpenAPI Specification](../docs/openapi.yaml)
- [WebSocket Protocol](../docs/websocket-protocol.md)
- [Quick Start Guide](QUICKSTART_BACKEND.md)
- [Implementation Summary](IMPLEMENTATION_COMPLETE.md)

## Contributing

When contributing to the backend:
- Follow the existing code structure
- Write tests for new features
- Update OpenAPI spec if adding/changing endpoints
- Run `pytest -v` before committing
- Follow PEP 8 style guidelines
- Add docstrings to new functions

## Quick Command Reference

### Essential Commands

```bash
# Setup
cd server && uv sync                              # Install dependencies

# Testing
uv run pytest -v                                  # Run all 48 tests
uv run pytest tests/test_integration.py -v        # Run 13 integration tests
./run_integration_tests.sh                        # Automated integration test runner

# Running
uv run python run.py                              # Start backend (port 3000)
cd ../client && npm start                         # Start frontend (port 3001)

# Health Check
curl http://localhost:3000/health                 # Check backend status
```

### Full Testing Workflow

```bash
# Terminal 1: Start backend
cd server
uv run python run.py

# Terminal 2: Run tests
cd server
uv run pytest -v                                  # All tests (48)
uv run pytest tests/test_integration.py -v        # Integration only (13)

# Terminal 3: Start frontend
cd client
npm start

# Browser: Open http://localhost:3001
```

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [TESTING_GUIDE.md](TESTING_GUIDE.md) for complete testing instructions
3. Review test files for usage examples (48 test cases)
4. Check API documentation in OpenAPI spec
5. Review integration tests for complete workflows

## License

MIT
