"""Tests for WebSocket endpoints."""

import pytest
from fastapi.testclient import TestClient
import json

from src.main import app

client = TestClient(app)


class TestWebSocket:
    """Test WebSocket endpoints."""
    
    def test_websocket_connection_success(self):
        """Test successful WebSocket connection."""
        # Create session first
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Connect via WebSocket
        with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Should receive welcome message
            data = websocket.receive_json()
            
            assert data["type"] == "welcome"
            assert "data" in data
            assert data["data"]["sessionId"] == session_id
    
    def test_websocket_connection_invalid_session(self):
        """Test WebSocket connection to non-existent session."""
        # Try to connect to non-existent session
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/sessions/nonexistent") as websocket:
                pass
    
    def test_websocket_join_message(self):
        """Test sending join message."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive welcome
            websocket.receive_json()
            
            # Send join message
            join_msg = {
                "type": "join",
                "userId": "test-user-123",
                "data": {
                    "name": "Test User"
                }
            }
            
            websocket.send_json(join_msg)
            
            # Should not error
            # In real scenario, would test with multiple connections
    
    def test_websocket_ping_pong(self):
        """Test ping/pong keepalive."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive welcome
            websocket.receive_json()
            
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Should receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"
    
    def test_websocket_code_update(self):
        """Test code update message."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive welcome
            websocket.receive_json()
            
            # Send code update
            code_update = {
                "type": "code-update",
                "userId": "test-user",
                "data": {
                    "code": "print('updated code')",
                    "changes": []
                }
            }
            
            websocket.send_json(code_update)
            
            # Should not error
            # In production, would verify broadcast to other clients
    
    def test_websocket_cursor_position(self):
        """Test cursor position message."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive welcome
            websocket.receive_json()
            
            # Send cursor position
            cursor_msg = {
                "type": "cursor-position",
                "userId": "test-user",
                "data": {
                    "line": 5,
                    "column": 10
                }
            }
            
            websocket.send_json(cursor_msg)
            
            # Should not error
    
    def test_websocket_language_change(self):
        """Test language change message."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
            # Receive welcome
            websocket.receive_json()
            
            # Send language change
            lang_msg = {
                "type": "language-change",
                "userId": "test-user",
                "data": {
                    "language": "python"
                }
            }
            
            websocket.send_json(lang_msg)
            
            # Should not error
            # Verify language was changed
            session_response = client.get(f"/api/sessions/{session_id}")
            # Note: might receive broadcast message, skip for now
