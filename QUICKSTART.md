# Code Interview Platform - Quick Start Guide

## 🚀 Getting Started

### Start the Application
```bash
npm start
```

The app will open at `http://localhost:3000`

## 📋 How to Use

### Create an Interview Session
1. Visit `http://localhost:3000`
2. Click **"Create New Interview Session"**
3. Copy and share the generated URL with candidates
4. Both interviewer and candidate can edit code in real-time

### Features Available

✅ **Real-Time Collaboration** - All connected users see changes instantly  
✅ **Syntax Highlighting** - JavaScript, Python, Java, C++  
✅ **Code Execution** - Run JavaScript code in the browser  
✅ **Shareable Links** - Easy session sharing with unique URLs  

## 🎯 In the Interview Session

- **Select Language**: Use the dropdown to choose programming language
- **Write Code**: Type in the editor - changes sync to all users
- **Run Code**: Click "▶️ Run Code" to execute JavaScript
- **Copy Link**: Share the session URL with the "📋 Copy Link" button
- **Monitor Status**: Green indicator shows connection status

## ⚠️ Important Notes

- **Only JavaScript can be executed** (other languages show syntax highlighting)
- **Sessions are temporary** - code is not saved when users disconnect
- **Best with 2-10 users** per session for optimal performance
- **WebRTC-based** - works peer-to-peer, no backend needed

## 🔧 Technology

- React 18 + Vite
- CodeMirror 6 (code editor)
- Y.js + WebRTC (real-time collaboration)
- React Router (routing)

## 📁 Key Files

- `src/pages/Home.jsx` - Landing page
- `src/pages/InterviewSession.jsx` - Interview session UI
- `src/components/CollaborativeEditor.jsx` - Collaborative code editor
