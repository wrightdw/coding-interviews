# WebSocket Protocol Specification

## Connection

**Endpoint:** `ws://localhost:3000/ws/sessions/{sessionId}`

**Connection Flow:**
1. Client connects to WebSocket endpoint with session ID
2. Client sends `join` message with user info
3. Server broadcasts `user-joined` to all participants
4. Client receives current session state

## Message Format

All messages are JSON objects with the following structure:

```json
{
  "type": "message-type",
  "timestamp": "2025-12-09T21:40:08Z",
  "userId": "user-abc123",
  "data": { /* message-specific data */ }
}
```

## Client → Server Messages

### 1. Join Session
```json
{
  "type": "join",
  "userId": "user-abc123",
  "data": {
    "name": "Anonymous User"
  }
}
```

### 2. Code Update
```json
{
  "type": "code-update",
  "userId": "user-abc123",
  "data": {
    "changes": [
      {
        "from": 0,
        "to": 5,
        "insert": "const"
      }
    ],
    "version": 42
  }
}
```

### 3. Cursor Position
```json
{
  "type": "cursor-position",
  "userId": "user-abc123",
  "data": {
    "line": 10,
    "column": 5,
    "selection": {
      "from": { "line": 10, "column": 5 },
      "to": { "line": 10, "column": 15 }
    }
  }
}
```

### 4. Language Change
```json
{
  "type": "language-change",
  "userId": "user-abc123",
  "data": {
    "language": "python"
  }
}
```

### 5. Ping (keepalive)
```json
{
  "type": "ping"
}
```

## Server → Client Messages

### 1. Welcome
Sent immediately after connection is established.
```json
{
  "type": "welcome",
  "timestamp": "2025-12-09T21:40:08Z",
  "data": {
    "sessionId": "92d3e5a5-2274-4cad-8884-4a06f5ade166",
    "currentCode": "// code content",
    "language": "javascript",
    "participants": [
      {
        "userId": "user-xyz",
        "name": "Interviewer"
      }
    ]
  }
}
```

### 2. User Joined
```json
{
  "type": "user-joined",
  "timestamp": "2025-12-09T21:40:08Z",
  "userId": "user-abc123",
  "data": {
    "name": "Candidate",
    "participantCount": 2
  }
}
```

### 3. User Left
```json
{
  "type": "user-left",
  "timestamp": "2025-12-09T21:40:08Z",
  "userId": "user-abc123",
  "data": {
    "participantCount": 1
  }
}
```

### 4. Code Update
Broadcast to all other participants when someone edits.
```json
{
  "type": "code-update",
  "timestamp": "2025-12-09T21:40:08Z",
  "userId": "user-abc123",
  "data": {
    "changes": [
      {
        "from": 0,
        "to": 5,
        "insert": "const"
      }
    ],
    "version": 42
  }
}
```

### 5. Cursor Position
Broadcast cursor updates from other users.
```json
{
  "type": "cursor-position",
  "timestamp": "2025-12-09T21:40:08Z",
  "userId": "user-abc123",
  "data": {
    "line": 10,
    "column": 5,
    "selection": {
      "from": { "line": 10, "column": 5 },
      "to": { "line": 10, "column": 15 }
    }
  }
}
```

### 6. Language Changed
```json
{
  "type": "language-changed",
  "timestamp": "2025-12-09T21:40:08Z",
  "userId": "user-abc123",
  "data": {
    "language": "python"
  }
}
```

### 7. Error
```json
{
  "type": "error",
  "timestamp": "2025-12-09T21:40:08Z",
  "data": {
    "code": "SESSION_NOT_FOUND",
    "message": "The requested session does not exist"
  }
}
```

### 8. Pong (keepalive response)
```json
{
  "type": "pong",
  "timestamp": "2025-12-09T21:40:08Z"
}
```

## Connection Management

### Keepalive
- Client should send `ping` every 30 seconds
- Server responds with `pong`
- Connection closed if no ping received for 60 seconds

### Disconnection
- Server sends `user-left` to remaining participants
- Clean up user resources
- Close WebSocket connection

### Reconnection
- Client can reconnect using same userId
- Server sends current state in `welcome` message
- Resume collaboration seamlessly

## Error Handling

### Session Not Found
```json
{
  "type": "error",
  "data": {
    "code": "SESSION_NOT_FOUND",
    "message": "The requested session does not exist"
  }
}
```
Connection is closed after error.

### Invalid Message Format
```json
{
  "type": "error",
  "data": {
    "code": "INVALID_MESSAGE",
    "message": "Message format is invalid"
  }
}
```
Connection remains open, client should retry.

### Rate Limiting
```json
{
  "type": "error",
  "data": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many messages sent"
  }
}
```
Connection remains open, client should slow down.

## Implementation Notes

### Y.js Integration
The current frontend uses Y.js with WebRTC for peer-to-peer collaboration. The backend can:

1. **Option A: WebSocket Bridge**
   - Implement WebSocket signaling server for Y.js
   - Act as signaling relay (replaces `wss://signaling.yjs.dev`)
   - Store session documents in database

2. **Option B: Centralized Sync**
   - Implement custom CRDT or use Y.js on server
   - All changes go through server
   - More control, easier to implement features like history

### Recommended Approach
Use **Option B** with Y.js on the server side:
- Install `yjs` and `y-websocket` on server
- Create WebSocket provider on server
- Persist Y.js documents to database
- Enable features like history, playback, and snapshots
