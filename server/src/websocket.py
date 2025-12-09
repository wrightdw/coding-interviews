"""WebSocket server for real-time collaboration."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from datetime import datetime, timezone
import uuid

from src.database import db

router = APIRouter()

# Store active connections per session
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections for sessions."""
    
    @staticmethod
    async def connect(session_id: str, websocket: WebSocket, user_id: str, name: str):
        """Connect a client to a session."""
        await websocket.accept()
        
        if session_id not in active_connections:
            active_connections[session_id] = set()
        
        active_connections[session_id].add(websocket)
        
        # Add participant to database
        db.add_participant(session_id, user_id, name)
        
        # Send welcome message
        session = db.get_session(session_id)
        code_data = db.get_code(session_id)
        participants = db.get_participants(session_id)
        
        welcome_msg = {
            "type": "welcome",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "sessionId": session_id,
                "currentCode": code_data["code"] if code_data else "",
                "language": session.language.value if session else "javascript",
                "participants": [
                    {
                        "userId": p.userId,
                        "name": p.name
                    }
                    for p in (participants or [])
                ]
            }
        }
        
        await websocket.send_json(welcome_msg)
        
        # Notify others
        user_joined_msg = {
            "type": "user-joined",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "userId": user_id,
            "data": {
                "name": name,
                "participantCount": len(active_connections[session_id])
            }
        }
        
        await ConnectionManager.broadcast(session_id, user_joined_msg, exclude=websocket)
    
    @staticmethod
    async def disconnect(session_id: str, websocket: WebSocket, user_id: str):
        """Disconnect a client from a session."""
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)
            
            if not active_connections[session_id]:
                del active_connections[session_id]
        
        # Remove participant from database
        db.remove_participant(session_id, user_id)
        
        # Notify others
        user_left_msg = {
            "type": "user-left",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "userId": user_id,
            "data": {
                "participantCount": len(active_connections.get(session_id, []))
            }
        }
        
        await ConnectionManager.broadcast(session_id, user_left_msg)
    
    @staticmethod
    async def broadcast(session_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast a message to all clients in a session."""
        if session_id not in active_connections:
            return
        
        disconnected = []
        
        for connection in active_connections[session_id]:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            active_connections[session_id].discard(conn)
    
    @staticmethod
    async def handle_message(session_id: str, websocket: WebSocket, message: dict, user_id: str):
        """Handle incoming WebSocket message."""
        msg_type = message.get("type")
        
        if msg_type == "ping":
            # Respond with pong
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        elif msg_type == "code-update":
            # Broadcast code update to others
            broadcast_msg = {
                "type": "code-update",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "userId": user_id,
                "data": message.get("data", {})
            }
            
            # Update code in database
            if "data" in message and "code" in message["data"]:
                session = db.get_session(session_id)
                if session:
                    db.save_code(
                        session_id,
                        message["data"]["code"],
                        session.language,
                        user_id
                    )
            
            await ConnectionManager.broadcast(session_id, broadcast_msg, exclude=websocket)
        
        elif msg_type == "cursor-position":
            # Broadcast cursor position
            broadcast_msg = {
                "type": "cursor-position",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "userId": user_id,
                "data": message.get("data", {})
            }
            
            await ConnectionManager.broadcast(session_id, broadcast_msg, exclude=websocket)
        
        elif msg_type == "language-change":
            # Broadcast language change
            new_language = message.get("data", {}).get("language")
            
            if new_language:
                db.update_session(session_id, language=new_language)
                
                broadcast_msg = {
                    "type": "language-changed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "userId": user_id,
                    "data": {"language": new_language}
                }
                
                db.add_history_entry(
                    session_id,
                    user_id,
                    "language-change",
                    f"Changed language to {new_language}"
                )
                
                await ConnectionManager.broadcast(session_id, broadcast_msg, exclude=websocket)


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time collaboration."""
    
    # Verify session exists
    session = db.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    # Accept connection but don't add participant yet
    await websocket.accept()
    
    if session_id not in active_connections:
        active_connections[session_id] = set()
    
    active_connections[session_id].add(websocket)
    
    # Send welcome message without adding participant
    code_data = db.get_code(session_id)
    participants = db.get_participants(session_id)
    
    welcome_msg = {
        "type": "welcome",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "sessionId": session_id,
            "currentCode": code_data["code"] if code_data else "",
            "language": session.language.value if session else "javascript",
            "participants": [
                {
                    "userId": p.userId,
                    "name": p.name
                }
                for p in (participants or [])
            ]
        }
    }
    
    await websocket.send_json(welcome_msg)
    
    user_id = None
    name = "Anonymous User"
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle join message - this is when we actually add the participant
            if message.get("type") == "join":
                user_id = message.get("userId", str(uuid.uuid4()))
                name = message.get("data", {}).get("name", "Anonymous User")
                
                # Add participant to database
                db.add_participant(session_id, user_id, name)
                
                # Notify others
                user_joined_msg = {
                    "type": "user-joined",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "userId": user_id,
                    "data": {
                        "name": name,
                        "participantCount": len(active_connections[session_id])
                    }
                }
                
                await ConnectionManager.broadcast(session_id, user_joined_msg, exclude=websocket)
            else:
                # Handle other messages
                await ConnectionManager.handle_message(
                    session_id,
                    websocket,
                    message,
                    user_id or str(uuid.uuid4())
                )
    
    except WebSocketDisconnect:
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)
            
            if not active_connections[session_id]:
                del active_connections[session_id]
        
        # Remove participant from database if they joined
        if user_id:
            db.remove_participant(session_id, user_id)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)
            
            if not active_connections[session_id]:
                del active_connections[session_id]
        
        # Remove participant from database if they joined
        if user_id:
            db.remove_participant(session_id, user_id)
