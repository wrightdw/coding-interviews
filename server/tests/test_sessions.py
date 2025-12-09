"""Tests for session endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestSessions:
    """Test session management endpoints."""
    
    def test_create_session_default(self):
        """Test creating a session with default parameters."""
        response = client.post("/api/sessions")
        
        assert response.status_code == 201
        data = response.json()
        
        assert "sessionId" in data
        assert data["language"] == "javascript"
        assert data["activeParticipants"] == 0
        assert "url" in data
        assert "createdAt" in data
        assert "expiresAt" in data
    
    def test_create_session_custom(self):
        """Test creating a session with custom parameters."""
        payload = {
            "language": "python",
            "title": "Test Interview",
            "expiresIn": 48
        }
        
        response = client.post("/api/sessions", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["language"] == "python"
        assert data["title"] == "Test Interview"
    
    def test_get_session(self):
        """Test getting session details."""
        # Create session first
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Get session
        response = client.get(f"/api/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["sessionId"] == session_id
    
    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        response = client.get("/api/sessions/nonexistent-id")
        
        assert response.status_code == 404
    
    def test_update_session(self):
        """Test updating session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Update session
        update_payload = {
            "language": "java",
            "title": "Updated Interview"
        }
        
        response = client.patch(f"/api/sessions/{session_id}", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "java"
        assert data["title"] == "Updated Interview"
    
    def test_delete_session(self):
        """Test deleting session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Delete session
        response = client.delete(f"/api/sessions/{session_id}")
        
        assert response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404
    
    def test_get_code(self):
        """Test getting code from session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Get code
        response = client.get(f"/api/sessions/{session_id}/code")
        
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "language" in data
        assert data["sessionId"] == session_id
    
    def test_save_code(self):
        """Test saving code snapshot."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Save code
        code_payload = {
            "code": "print('Hello, World!')",
            "language": "python"
        }
        
        response = client.post(f"/api/sessions/{session_id}/code", json=code_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "snapshotId" in data
        assert "savedAt" in data
        assert data["sessionId"] == session_id
        
        # Verify code was saved
        get_response = client.get(f"/api/sessions/{session_id}/code")
        assert get_response.json()["code"] == code_payload["code"]
