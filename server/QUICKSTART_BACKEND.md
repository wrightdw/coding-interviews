# Quick Start Guide - FastAPI Backend

## Installation and Testing

```bash
cd server

# Make script executable
chmod +x setup_and_test.sh

# Run setup and tests
./setup_and_test.sh
```

## Manual Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Run Tests

```bash
# All tests
uv run pytest

# Verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=src
```

### 3. Start Server

```bash
uv run python run.py
```

Server runs on `http://localhost:3000`

## Verify Installation

```bash
# Check health endpoint
curl http://localhost:3000/health

# Create a session
curl -X POST http://localhost:3000/api/sessions

# View API docs
open http://localhost:3000/docs
```

## Test Commands

```bash
# Run specific test file
uv run pytest tests/test_sessions.py

# Run tests matching pattern
uv run pytest -k "test_create_session"

# Show test coverage
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Development Workflow

```bash
# Start with hot reload
uv run python run.py

# In another terminal, run tests on changes
uv run pytest --watch
```

## Troubleshooting

### Port 3000 already in use

```bash
# Change port in run.py or:
uv run uvicorn src.main:app --reload --port 3001
```

### Import errors

```bash
# Reinstall dependencies
rm -rf .venv
uv sync
```

### Test failures

```bash
# Run tests with detailed output
uv run pytest -vv --tb=long
```

## What's Implemented

✅ **REST API**
- Session management (create, get, update, delete)
- Code snapshots and retrieval
- Participant tracking
- Session history
- Python code execution

✅ **WebSocket**
- Real-time collaboration
- User join/leave events
- Code synchronization
- Cursor position sharing
- Language changes

✅ **Tests**
- 40+ test cases
- REST endpoint coverage
- WebSocket testing
- Code execution testing
- Error handling

✅ **Documentation**
- OpenAPI/Swagger UI
- ReDoc interface
- Comprehensive README

## Next: Connect Frontend

See `INTEGRATION_GUIDE.md` for instructions on connecting the React frontend to this backend.
