"""Tests for collaboration endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestCollaboration:
    """Test collaboration endpoints."""
    
    def test_get_participants_empty(self):
        """Test getting participants for new session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Get participants
        response = client.get(f"/api/sessions/{session_id}/participants")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sessionId"] == session_id
        assert data["participants"] == []
    
    def test_get_participants_not_found(self):
        """Test getting participants for non-existent session."""
        response = client.get("/api/sessions/nonexistent/participants")
        
        assert response.status_code == 404
    
    def test_get_history_empty(self):
        """Test getting history for new session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Get history
        response = client.get(f"/api/sessions/{session_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["sessionId"] == session_id
        assert isinstance(data["history"], list)
    
    def test_get_history_with_limit(self):
        """Test getting history with limit parameter."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Get history with limit
        response = client.get(f"/api/sessions/{session_id}/history?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["history"]) <= 10
    
    def test_get_history_after_code_save(self):
        """Test that history is recorded after code save."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Save code
        code_payload = {
            "code": "print('test')",
            "language": "python"
        }
        client.post(f"/api/sessions/{session_id}/code", json=code_payload)
        
        # Get history
        response = client.get(f"/api/sessions/{session_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have at least one history entry
        assert len(data["history"]) > 0
        assert data["history"][0]["changeType"] == "snapshot"
    
    def test_get_history_not_found(self):
        """Test getting history for non-existent session."""
        response = client.get("/api/sessions/nonexistent/history")
        
        assert response.status_code == 404
    
    def test_history_limit_validation(self):
        """Test history limit validation."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Try invalid limit (too high)
        response = client.get(f"/api/sessions/{session_id}/history?limit=200")
        
        assert response.status_code == 422  # Validation error
        
        # Try invalid limit (too low)
        response = client.get(f"/api/sessions/{session_id}/history?limit=0")
        
        assert response.status_code == 422  # Validation error
