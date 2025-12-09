# Testing Guide - Coding Interview Platform

Complete guide for testing the client-server integration and all application functionality.

## 📋 Table of Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Running All Tests](#running-all-tests)
3. [Integration Tests](#integration-tests)
4. [Manual Testing](#manual-testing)
5. [Test Scenarios](#test-scenarios)
6. [Troubleshooting Tests](#troubleshooting-tests)

## Test Suite Overview

### Test Coverage

The application includes **48 comprehensive test cases**:

| Test Suite | Tests | Description |
|------------|-------|-------------|
| Unit Tests - Sessions | 10 | Session CRUD operations |
| Unit Tests - Execution | 9 | Code execution functionality |
| Unit Tests - Collaboration | 7 | Collaboration endpoints |
| Unit Tests - WebSocket | 7 | WebSocket communication |
| Unit Tests - Main | 4 | Health checks and CORS |
| **Integration Tests** | **13** | **Complete workflows** |
| **Total** | **48** | **Full coverage** |

### Integration Test Scenarios

The integration tests verify complete client-server workflows:

1. ✅ **Complete Interview Workflow** - End-to-end session creation, code editing, execution
2. ✅ **Multi-User Collaboration** - Multiple users in same session via WebSocket
3. ✅ **Language Switching** - Changing programming language mid-session
4. ✅ **Code Execution Feedback Loop** - Iterative code editing and execution
5. ✅ **Session Persistence** - Data persists across WebSocket reconnects
6. ✅ **Concurrent Code Updates** - Handling simultaneous edits from multiple users
7. ✅ **Participant Tracking** - Join/leave event handling
8. ✅ **Cursor Synchronization** - Real-time cursor position sharing
9. ✅ **Error Recovery** - Handling invalid requests and errors gracefully
10. ✅ **Full Interview Simulation** - Complete interview from start to finish
11. ✅ **Empty Code Execution** - Edge case handling
12. ✅ **Very Long Code** - Large payload handling
13. ✅ **Rapid Session Creation** - Stress testing session creation

## Running All Tests

### Quick Test Commands

```bash
# Navigate to server directory
cd server

# Run ALL tests (48 tests)
uv run pytest -v

# Run with coverage report
uv run pytest --cov=src --cov-report=html --cov-report=term

# Run only integration tests (13 tests)
uv run pytest tests/test_integration.py -v

# Run specific test class
uv run pytest tests/test_integration.py::TestClientServerIntegration -v

# Run specific test method
uv run pytest tests/test_integration.py::TestClientServerIntegration::test_complete_interview_workflow -v
```

### Using the Test Script

```bash
# Make script executable
chmod +x run_integration_tests.sh

# Run integration tests
./run_integration_tests.sh
```

### Test Output Options

```bash
# Verbose output with details
uv run pytest -v

# Show print statements
uv run pytest -v -s

# Stop on first failure
uv run pytest -x

# Run last failed tests
uv run pytest --lf

# Show test durations
uv run pytest --durations=10

# Quiet mode (only show summary)
uv run pytest -q

# Match pattern (run tests matching keyword)
uv run pytest -k "workflow"
uv run pytest -k "collaboration"
uv run pytest -k "websocket"
```

## Integration Tests

### What Integration Tests Cover

Integration tests verify that the **client and server work together correctly** by:

1. **Creating sessions** via REST API
2. **Connecting via WebSocket** for real-time communication
3. **Saving and retrieving code** through API endpoints
4. **Executing code** and checking results
5. **Managing participants** across multiple connections
6. **Tracking session history** of all changes
7. **Handling errors** and edge cases

### Running Integration Tests

```bash
cd server

# Run all integration tests
uv run pytest tests/test_integration.py -v

# Run specific integration test class
uv run pytest tests/test_integration.py::TestClientServerIntegration -v

# Run edge case tests
uv run pytest tests/test_integration.py::TestClientServerEdgeCases -v
```

### Understanding Test Results

```bash
# Example output:
tests/test_integration.py::TestClientServerIntegration::test_complete_interview_workflow PASSED [ 7%]
tests/test_integration.py::TestClientServerIntegration::test_multi_user_collaboration_workflow PASSED [15%]
...

# Summary:
========== 13 passed in 2.45s ==========
```

- ✅ **PASSED** - Test successful
- ❌ **FAILED** - Test failed (see traceback)
- ⚠️ **SKIPPED** - Test skipped (expected)
- 🔄 **XFAIL** - Expected failure (known issue)

## Manual Testing

### Full Application Test

#### Step 1: Start Backend

```bash
# Terminal 1
cd server
uv sync
uv run python run.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000
```

#### Step 2: Run Integration Tests

```bash
# Terminal 2
cd server
uv run pytest tests/test_integration.py -v
```

Expected: All 13 tests should pass

#### Step 3: Start Frontend

```bash
# Terminal 3
cd client
npm start
```

Expected output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: use --host to expose
```

#### Step 4: Manual Browser Testing

1. Open `http://localhost:3001`
2. Click "Create New Interview Session"
3. Should navigate to `/interview/{sessionId}`
4. Try typing code in the editor
5. Select different languages
6. Click "Run Code" (Python only)
7. Open same URL in another browser/tab
8. Verify real-time synchronization

### API Testing with curl

#### Create Session
```bash
curl -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "title": "Test Session"}'
```

Expected response:
```json
{
  "sessionId": "uuid-here",
  "url": "http://localhost:3001/interview/uuid-here",
  "language": "python",
  "title": "Test Session",
  "createdAt": "2024-01-01T12:00:00",
  "expiresAt": "2024-01-02T12:00:00"
}
```

#### Get Session
```bash
curl http://localhost:3000/api/sessions/{sessionId}
```

#### Execute Code
```bash
curl -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello World\")",
    "language": "python",
    "timeout": 5
  }'
```

Expected response:
```json
{
  "success": true,
  "stdout": "Hello World\n",
  "stderr": "",
  "error": null,
  "executionTime": 0.123
}
```

#### Health Check
```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### WebSocket Testing with wscat

```bash
# Install wscat if needed
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:3000/ws/sessions/{sessionId}

# You should receive welcome message:
# < {"type":"welcome","data":{...}}

# Send join message:
# > {"type":"join","userId":"user-1","data":{"name":"Test User"}}

# Send code update:
# > {"type":"code-update","userId":"user-1","data":{"code":"print('test')"}}

# Send ping:
# > {"type":"ping"}
# < {"type":"pong"}
```

## Test Scenarios

### Scenario 1: Single User Interview

**Objective**: Test basic interview session creation and code execution

**Steps**:
1. Run: `uv run pytest tests/test_integration.py::TestClientServerIntegration::test_complete_interview_workflow -v`
2. Test creates session, saves code, executes Python, checks history, deletes session

**Expected**: Test passes, all operations successful

### Scenario 2: Multi-User Collaboration

**Objective**: Test real-time collaboration between users

**Steps**:
1. Run: `uv run pytest tests/test_integration.py::TestClientServerIntegration::test_multi_user_collaboration_workflow -v`
2. Test connects 2 users via WebSocket, shares code updates, verifies participant tracking

**Expected**: Test passes, both users see updates

### Scenario 3: Language Switching

**Objective**: Test changing programming language mid-session

**Steps**:
1. Run: `uv run pytest tests/test_integration.py::TestClientServerIntegration::test_language_switching_workflow -v`
2. Test creates JavaScript session, switches to Python via WebSocket, verifies persistence

**Expected**: Test passes, language change persists

### Scenario 4: Error Handling

**Objective**: Test error recovery and invalid inputs

**Steps**:
1. Run: `uv run pytest tests/test_integration.py::TestClientServerIntegration::test_error_recovery_workflow -v`
2. Test sends invalid session IDs, non-existent sessions, invalid timeouts

**Expected**: Test passes, appropriate error responses returned

### Scenario 5: Complete Interview Simulation

**Objective**: Simulate real interview from start to finish

**Steps**:
1. Run: `uv run pytest tests/test_integration.py::TestClientServerIntegration::test_full_interview_simulation -v`
2. Test runs complete interview: create → connect → code → execute → review → cleanup

**Expected**: Test passes, full workflow successful

## Troubleshooting Tests

### Tests Fail on First Run

**Problem**: Tests fail with "connection refused" or similar

**Solution**:
```bash
# Ensure dependencies are installed
cd server
uv sync

# Ensure no conflicting processes
lsof -i :3000
kill -9 <PID>  # if needed

# Run tests again
uv run pytest -v
```

### WebSocket Tests Fail

**Problem**: WebSocket connection tests timeout or fail

**Solution**:
```bash
# Check if port is blocked
lsof -i :3000

# Verify FastAPI is configured correctly
grep -r "CORSMiddleware" src/main.py

# Run WebSocket tests specifically
uv run pytest tests/test_websocket.py -v -s
```

### Integration Tests Timeout

**Problem**: Tests hang or timeout

**Solution**:
```bash
# Run with shorter timeout
uv run pytest tests/test_integration.py --timeout=30

# Run with verbose output to see where it hangs
uv run pytest tests/test_integration.py -v -s

# Run one test at a time
uv run pytest tests/test_integration.py::TestClientServerIntegration::test_complete_interview_workflow -v
```

### Coverage Report Not Generated

**Problem**: `--cov` flag doesn't generate report

**Solution**:
```bash
# Install coverage explicitly
uv pip install pytest-cov

# Generate HTML report
uv run pytest --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Tests Pass but Manual Testing Fails

**Problem**: Automated tests pass but browser testing doesn't work

**Solution**:
```bash
# 1. Verify backend is running
curl http://localhost:3000/health

# 2. Check backend logs for errors
cd server
uv run python run.py  # Check console output

# 3. Verify frontend is connecting to correct backend
cd client
grep -r "localhost:3000" src/

# 4. Check browser console for errors
# Open DevTools (F12) → Console tab

# 5. Verify WebSocket connection
# DevTools → Network tab → WS filter → Check connection status
```

### Import Errors

**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name ".pytest_cache" -exec rm -r {} +

# Reinstall dependencies
uv sync --reinstall

# Verify installation
uv pip list

# Run tests
uv run pytest -v
```

### Database Errors

**Problem**: Tests fail with database-related errors

**Solution**:
```bash
# Current implementation uses mock database (in-memory)
# No real database needed

# If seeing persistence errors, this is expected
# Mock database resets between test runs

# To persist data across runs, implement real database:
# See server/README.md "Next Steps" section
```

## Test Best Practices

### Before Committing

```bash
# 1. Run all tests
uv run pytest -v

# 2. Check coverage
uv run pytest --cov=src --cov-report=term

# 3. Run integration tests specifically
uv run pytest tests/test_integration.py -v

# 4. Verify no warnings
uv run pytest -v --tb=short

# 5. Check code quality (if using)
ruff check src/
black --check src/
```

### Writing New Tests

When adding features, add tests:

```python
# tests/test_integration.py

def test_new_feature_workflow(self):
    """Test description of what this workflow does."""
    # 1. Setup - Create necessary resources
    response = client.post("/api/sessions")
    session_id = response.json()["sessionId"]
    
    # 2. Action - Perform the test action
    result = client.post(f"/api/some-new-endpoint/{session_id}")
    
    # 3. Assert - Verify expected behavior
    assert result.status_code == 200
    assert result.json()["expected_field"] == "expected_value"
    
    # 4. Cleanup - Clean up resources
    client.delete(f"/api/sessions/{session_id}")
```

### Continuous Integration

For CI/CD pipelines:

```bash
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: cd server && uv sync
      - name: Run tests
        run: cd server && uv run pytest -v --cov=src
```

## Summary of All Commands

```bash
# Setup
cd server && uv sync

# Run all tests
uv run pytest -v

# Run integration tests only
uv run pytest tests/test_integration.py -v

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_integration.py::TestClientServerIntegration::test_complete_interview_workflow -v

# Start backend
uv run python run.py

# Start frontend (separate terminal)
cd client && npm start

# Manual API test
curl http://localhost:3000/health

# WebSocket test
wscat -c ws://localhost:3000/ws/sessions/{id}
```

## Quick Reference

| Task | Command |
|------|---------|
| All tests | `uv run pytest -v` |
| Integration only | `uv run pytest tests/test_integration.py -v` |
| With coverage | `uv run pytest --cov=src` |
| Stop on fail | `uv run pytest -x` |
| Specific test | `uv run pytest -k "workflow"` |
| Show prints | `uv run pytest -v -s` |
| Start backend | `uv run python run.py` |
| Start frontend | `cd client && npm start` |
| Health check | `curl localhost:3000/health` |

---

**For more information, see:**
- [Backend README](README.md) - Complete backend documentation
- [Root README](../ROOT_README.md) - Full application overview
- [OpenAPI Spec](openapi.yaml) - API documentation
