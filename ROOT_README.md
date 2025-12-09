# Coding Interview Platform

A real-time collaborative coding interview platform with synchronized editing, code execution, and multi-language support.

## 🎯 Features

- **Real-time Collaboration**: Multiple users can code together with synchronized editing
- **Multi-Language Support**: Syntax highlighting for JavaScript, Python, Java, and C++
- **Code Execution**: Run Python code directly in the browser with sandboxed execution
- **Session Management**: Create shareable interview sessions with unique URLs
- **WebSocket Communication**: Real-time updates for code changes, cursor positions, and participants
- **Modern UI**: Clean, responsive interface built with React

## 🏗️ Architecture

### Full-Stack Application

```
coding-interview-platform/
├── client/                  # React frontend
│   ├── src/
│   │   ├── components/     # CollaborativeEditor
│   │   ├── pages/          # Home, InterviewSession
│   │   └── App.jsx         # Main routing
│   └── package.json
│
└── server/                  # FastAPI backend
    ├── src/
    │   ├── main.py         # FastAPI app
    │   ├── models.py       # Pydantic models
    │   ├── database.py     # Mock database
    │   ├── websocket.py    # WebSocket server
    │   └── routers/        # API endpoints
    ├── tests/              # 48 test cases
    └── pyproject.toml      # Dependencies
```

### Technology Stack

**Frontend:**
- React 18.2 with Vite
- CodeMirror 6 (code editor)
- Y.js (CRDT for collaboration)
- React Router (navigation)
- WebSockets (real-time communication)

**Backend:**
- FastAPI 0.115+ (Python web framework)
- WebSockets (real-time bidirectional communication)
- Pydantic 2.10+ (data validation)
- uv (Python package manager)
- pytest (testing framework)

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (for frontend)
- **Python 3.11+** (for backend)
- **uv** (Python package manager)

### Installation

#### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd coding-interview-platform

# Setup backend
cd server
uv sync
uv run pytest -v    # Verify installation with tests

# Setup frontend (in a new terminal)
cd client
npm install
```

### Running the Application

#### Terminal 1: Start Backend

```bash
cd server
uv run python run.py
# Server starts on http://localhost:3000
```

#### Terminal 2: Start Frontend

```bash
cd client
npm start
# Frontend starts on http://localhost:3001
```

#### Terminal 3: Run Tests (Optional)

```bash
cd server
uv run pytest -v                         # All tests
uv run pytest tests/test_integration.py  # Integration tests only
```

### Access the Application

Open your browser to **http://localhost:3001**

## 📖 Usage

### Creating an Interview Session

1. Open the application
2. Click "Create New Interview Session"
3. Share the generated URL with participants
4. Start coding together in real-time!

### Using the Editor

- **Select Language**: Choose from JavaScript, Python, Java, or C++
- **Write Code**: Type in the collaborative editor
- **Run Code**: Click "Run Code" (Python only for now)
- **Share Link**: Click "Copy Interview Link" to invite others

### Real-time Features

- **Live Editing**: See others' code changes instantly
- **Cursor Tracking**: View other participants' cursor positions
- **Language Sync**: Language changes propagate to all users
- **Participant List**: See who's currently in the session

## 🧪 Testing

### Backend Tests

```bash
cd server

# Run all tests (48 total)
uv run pytest -v

# Run specific test suites
uv run pytest tests/test_sessions.py      # Session management (10 tests)
uv run pytest tests/test_execution.py     # Code execution (9 tests)
uv run pytest tests/test_collaboration.py # Collaboration (7 tests)
uv run pytest tests/test_websocket.py     # WebSocket (7 tests)
uv run pytest tests/test_integration.py   # Integration (13 tests)

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run tests matching pattern
uv run pytest -k "workflow"
```

### Test Coverage

- ✅ **Unit Tests**: 28 tests for individual endpoints and functions
- ✅ **Integration Tests**: 13 tests for complete workflows
- ✅ **WebSocket Tests**: 7 tests for real-time communication
- ✅ **Total**: 48 comprehensive test cases

### Integration Test Scenarios

- Complete interview session lifecycle
- Multi-user collaboration
- Language switching workflow
- Code execution feedback loop
- Session persistence across reconnects
- Concurrent code updates
- Participant tracking lifecycle
- Cursor position synchronization
- Error recovery
- Full interview simulation
- Edge cases (empty code, long code, rapid creation)

## 📡 API Documentation

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create new interview session |
| GET | `/api/sessions/{id}` | Get session details |
| PATCH | `/api/sessions/{id}` | Update session (language, title) |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/api/sessions/{id}/code` | Get current code |
| POST | `/api/sessions/{id}/code` | Save code snapshot |
| POST | `/api/execute` | Execute code (Python) |
| GET | `/api/sessions/{id}/participants` | Get active participants |
| GET | `/api/sessions/{id}/history` | Get session history |
| GET | `/health` | Health check |

### WebSocket Endpoint

**Endpoint**: `ws://localhost:3000/ws/sessions/{sessionId}`

**Message Types**:
- `join` - User joins session
- `leave` - User leaves session
- `code-update` - Code content changed
- `cursor-position` - Cursor position update
- `language-change` - Programming language changed
- `ping/pong` - Keep-alive heartbeat

## 🛠️ Development

### Project Structure

```
client/src/
├── components/
│   └── CollaborativeEditor.jsx    # CodeMirror + Y.js editor
├── pages/
│   ├── Home.jsx                   # Landing page
│   └── InterviewSession.jsx       # Main interview UI
├── App.jsx                        # Routing
└── index.jsx                      # Entry point

server/src/
├── main.py                        # FastAPI application
├── models.py                      # 9 Pydantic models
├── database.py                    # Mock database
├── websocket.py                   # Connection manager
└── routers/
    ├── sessions.py                # Session endpoints
    ├── collaboration.py           # Collaboration endpoints
    └── execute.py                 # Code execution
```

### Development Workflow

```bash
# 1. Make changes to code
# 2. Run tests
cd server && uv run pytest -v

# 3. Test integration
uv run pytest tests/test_integration.py -v

# 4. Start server (auto-reload)
uv run python run.py

# 5. Start frontend (auto-reload)
cd client && npm start

# 6. Test in browser at http://localhost:3001
```

### Adding New Features

1. **Backend**: Add routes in `server/src/routers/`
2. **Frontend**: Add components in `client/src/components/`
3. **Tests**: Add tests in `server/tests/`
4. **API**: Update OpenAPI spec if endpoints change

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
uv run uvicorn src.main:app --port 8000
```

### Frontend Won't Start

```bash
# Clear node_modules and reinstall
cd client
rm -rf node_modules package-lock.json
npm install
npm start
```

### Tests Failing

```bash
# Clear cache and reinstall
cd server
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name ".pytest_cache" -exec rm -r {} +
uv sync --reinstall
uv run pytest -v
```

### WebSocket Connection Issues

- Ensure backend is running on port 3000
- Check CORS configuration in `server/src/main.py`
- Verify WebSocket URL: `ws://localhost:3000/ws/sessions/{id}`
- Check browser console for errors

### Code Execution Not Working

- Only Python execution is implemented
- Check timeout settings (max 10 seconds)
- Verify Python environment is set up correctly
- Check `server/src/routers/execute.py` for implementation

## 📚 Documentation

- **[Backend README](server/README.md)**: Complete backend documentation
- **[OpenAPI Spec](docs/openapi.yaml)**: Full API specification
- **[WebSocket Protocol](docs/websocket-protocol.md)**: WebSocket message format
- **[Quick Start Guide](server/QUICKSTART_BACKEND.md)**: Fast backend setup
- **[Implementation Details](server/IMPLEMENTATION_COMPLETE.md)**: Technical summary

## 🔒 Security Notes

### Current Implementation (Development Only)

⚠️ **Not Production Ready**
- No authentication/authorization
- Code execution uses simple subprocess
- No rate limiting
- CORS allows all localhost origins
- Mock in-memory database (data not persistent)

### Production Requirements

For production deployment, implement:
- ✅ JWT authentication and authorization
- ✅ Docker containers for code execution sandboxing
- ✅ Rate limiting (per user/IP)
- ✅ HTTPS/WSS for all connections
- ✅ Input validation and sanitization
- ✅ Real database (PostgreSQL/MongoDB)
- ✅ Redis for session management
- ✅ User quotas and resource limits
- ✅ Monitoring and logging
- ✅ GDPR compliance and data privacy

## 🚢 Deployment

### Backend Deployment

```bash
# Production build
cd server
uv sync

# Run with production server
uv run uvicorn src.main:app --host 0.0.0.0 --port 3000 --workers 4
```

### Frontend Deployment

```bash
# Build for production
cd client
npm run build

# Serve build folder with any static server
# Update VITE_API_URL to production backend URL
```

### Environment Variables

**Backend** (`server/.env`):
```env
PORT=3000
CORS_ORIGINS=http://localhost:3001,https://yourdomain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

**Frontend** (`client/.env`):
```env
VITE_API_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3000
```

## 🗺️ Roadmap

### Completed ✅
- [x] React frontend with CodeMirror
- [x] Real-time collaboration with Y.js
- [x] FastAPI backend with WebSocket
- [x] Session management API
- [x] Python code execution
- [x] Comprehensive test suite (48 tests)
- [x] Integration tests for client-server interaction

### In Progress 🚧
- [ ] Connect frontend to backend API
- [ ] Replace WebRTC with WebSocket in frontend
- [ ] Add real database (PostgreSQL)

### Planned 📋
- [ ] Authentication and authorization
- [ ] Multi-language code execution (JavaScript, Java, C++)
- [ ] Code execution in Docker containers
- [ ] Session recording and playback
- [ ] Video/audio chat integration
- [ ] Code review and feedback features
- [ ] Admin dashboard
- [ ] Analytics and insights

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new features
4. Ensure all tests pass (`uv run pytest -v`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Follow React best practices
- Write tests for all new features
- Update documentation for API changes
- Keep dependencies up to date

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 👥 Authors

- Initial work - Collaborative Interview Platform Team

## 🙏 Acknowledgments

- **CodeMirror** - Excellent code editor
- **Y.js** - CRDT implementation for collaboration
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **uv** - Fast Python package manager

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review test files for usage examples
3. Check API documentation
4. Open an issue on GitHub

---

**Happy Coding! 🎉**
