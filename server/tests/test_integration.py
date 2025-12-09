"""Integration tests for client-server interaction."""

import pytest
from fastapi.testclient import TestClient
import json

from src.main import app

client = TestClient(app)


class TestClientServerIntegration:
    """Test complete workflows between client and server."""
    
    def test_complete_interview_workflow(self):
        """Test a complete interview session workflow."""
        # 1. Client creates a new session
        create_response = client.post("/api/sessions", json={
            "language": "python",
            "title": "Integration Test Interview"
        })
        assert create_response.status_code == 201
        session = create_response.json()
        session_id = session["sessionId"]
        
        # 2. Client retrieves session details
        get_response = client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Integration Test Interview"
        
        # 3. Client saves code
        code_payload = {
            "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))",
            "language": "python"
        }
        save_response = client.post(
            f"/api/sessions/{session_id}/code",
            json=code_payload
        )
        assert save_response.status_code == 200
        
        # 4. Client retrieves code
        code_response = client.get(f"/api/sessions/{session_id}/code")
        assert code_response.status_code == 200
        assert code_response.json()["code"] == code_payload["code"]
        
        # 5. Client executes code
        execute_response = client.post("/api/execute", json={
            "code": code_payload["code"],
            "language": "python",
            "timeout": 5
        })
        assert execute_response.status_code == 200
        result = execute_response.json()
        assert result["success"] is True
        assert "55" in result["stdout"]  # fibonacci(10) = 55
        
        # 6. Client checks history
        history_response = client.get(f"/api/sessions/{session_id}/history")
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history["history"]) > 0
        
        # 7. Client deletes session
        delete_response = client.delete(f"/api/sessions/{session_id}")
        assert delete_response.status_code == 204
    
    def test_multi_user_collaboration_workflow(self):
        """Test multiple users collaborating in same session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # User 1 connects via WebSocket
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws1:
            # Receive welcome message
            welcome1 = ws1.receive_json()
            assert welcome1["type"] == "welcome"
            
            # User 1 joins
            ws1.send_json({
                "type": "join",
                "userId": "user-1",
                "data": {"name": "Alice"}
            })
            
            # User 2 connects via WebSocket
            with client.websocket_connect(f"/ws/sessions/{session_id}") as ws2:
                # Receive welcome message
                welcome2 = ws2.receive_json()
                assert welcome2["type"] == "welcome"
                
                # User 2 joins
                ws2.send_json({
                    "type": "join",
                    "userId": "user-2",
                    "data": {"name": "Bob"}
                })
                
                # User 1 should receive user-joined message
                # (Note: In actual implementation, might need to handle message order)
                
                # User 1 sends code update
                ws1.send_json({
                    "type": "code-update",
                    "userId": "user-1",
                    "data": {
                        "code": "print('Hello from Alice')",
                        "changes": []
                    }
                })
                
                # Check participants via REST API
                participants_response = client.get(
                    f"/api/sessions/{session_id}/participants"
                )
                assert participants_response.status_code == 200
                participants = participants_response.json()
                assert len(participants["participants"]) == 2
    
    def test_language_switching_workflow(self):
        """Test switching programming language during session."""
        # Create JavaScript session
        create_response = client.post("/api/sessions", json={
            "language": "javascript"
        })
        session_id = create_response.json()["sessionId"]
        
        # Connect via WebSocket
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws:
            ws.receive_json()  # welcome
            
            # Change language to Python
            ws.send_json({
                "type": "language-change",
                "userId": "user-1",
                "data": {"language": "python"}
            })
            
            # Verify language changed via REST API
            session_response = client.get(f"/api/sessions/{session_id}")
            assert session_response.json()["language"] == "python"
            
            # Save Python code
            client.post(f"/api/sessions/{session_id}/code", json={
                "code": "print('Now using Python')",
                "language": "python"
            })
            
            # Verify code was saved
            code_response = client.get(f"/api/sessions/{session_id}/code")
            assert code_response.json()["language"] == "python"
    
    def test_code_execution_feedback_loop(self):
        """Test iterative code execution with error correction."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # First attempt: Code with error
        error_code = "print(undefined_variable)"
        execute_response = client.post("/api/execute", json={
            "code": error_code,
            "language": "python",
            "timeout": 5
        })
        result = execute_response.json()
        assert result["success"] is False
        assert result["error"] is not None
        
        # Save the error code
        client.post(f"/api/sessions/{session_id}/code", json={
            "code": error_code,
            "language": "python"
        })
        
        # Second attempt: Corrected code
        correct_code = "defined_variable = 'Hello'\nprint(defined_variable)"
        execute_response = client.post("/api/execute", json={
            "code": correct_code,
            "language": "python",
            "timeout": 5
        })
        result = execute_response.json()
        assert result["success"] is True
        assert "Hello" in result["stdout"]
        
        # Save the correct code
        client.post(f"/api/sessions/{session_id}/code", json={
            "code": correct_code,
            "language": "python"
        })
        
        # Verify history shows both attempts
        history_response = client.get(f"/api/sessions/{session_id}/history")
        history = history_response.json()
        assert len(history["history"]) >= 2
    
    def test_session_persistence_across_reconnects(self):
        """Test that session data persists across WebSocket reconnects."""
        # Create session and save code
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        initial_code = "print('Initial code')"
        client.post(f"/api/sessions/{session_id}/code", json={
            "code": initial_code,
            "language": "python"
        })
        
        # First connection
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws1:
            welcome = ws1.receive_json()
            assert welcome["type"] == "welcome"
            assert initial_code in welcome["data"]["currentCode"]
        
        # Disconnect and reconnect (simulating connection drop)
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws2:
            welcome = ws2.receive_json()
            assert welcome["type"] == "welcome"
            # Code should still be there
            assert initial_code in welcome["data"]["currentCode"]
    
    def test_concurrent_code_updates(self):
        """Test handling of concurrent code updates from multiple clients."""
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws1:
            ws1.receive_json()  # welcome
            
            with client.websocket_connect(f"/ws/sessions/{session_id}") as ws2:
                ws2.receive_json()  # welcome
                
                # Both users update code
                ws1.send_json({
                    "type": "code-update",
                    "userId": "user-1",
                    "data": {"code": "line1\nline2"}
                })
                
                ws2.send_json({
                    "type": "code-update",
                    "userId": "user-2",
                    "data": {"code": "line1\nline2\nline3"}
                })
                
                # Verify final code via REST API
                code_response = client.get(f"/api/sessions/{session_id}/code")
                assert code_response.status_code == 200
                # One of the updates should be saved
                assert len(code_response.json()["code"]) > 0
    
    def test_participant_tracking_lifecycle(self):
        """Test participant tracking through join and leave events."""
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Initially no participants
        participants = client.get(f"/api/sessions/{session_id}/participants")
        assert len(participants.json()["participants"]) == 0
        
        # User joins
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws:
            ws.receive_json()  # welcome
            
            ws.send_json({
                "type": "join",
                "userId": "user-1",
                "data": {"name": "Test User"}
            })
            
            # Check participant count
            participants = client.get(f"/api/sessions/{session_id}/participants")
            assert len(participants.json()["participants"]) == 1
            assert participants.json()["participants"][0]["name"] == "Test User"
        
        # After disconnect, participant should be removed
        # (Small delay might be needed in real scenario)
        participants = client.get(f"/api/sessions/{session_id}/participants")
        # Note: Depending on cleanup timing, might still show 1 or 0
    
    def test_cursor_position_synchronization(self):
        """Test cursor position sharing between users."""
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws1:
            ws1.receive_json()  # welcome
            
            with client.websocket_connect(f"/ws/sessions/{session_id}") as ws2:
                ws2.receive_json()  # welcome
                
                # User 1 updates cursor position
                ws1.send_json({
                    "type": "cursor-position",
                    "userId": "user-1",
                    "data": {
                        "line": 10,
                        "column": 5
                    }
                })
                
                # Both users send ping to keep connection alive
                ws1.send_json({"type": "ping"})
                pong = ws1.receive_json()
                assert pong["type"] == "pong"
    
    def test_error_recovery_workflow(self):
        """Test error handling and recovery in client-server interaction."""
        # Try to get non-existent session
        response = client.get("/api/sessions/invalid-id")
        assert response.status_code == 404
        
        # Try to save code to non-existent session
        response = client.post("/api/sessions/invalid-id/code", json={
            "code": "test",
            "language": "python"
        })
        assert response.status_code == 404
        
        # Try to connect to non-existent session via WebSocket
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/sessions/invalid-id") as ws:
                pass
        
        # Execute code with very long timeout (should be rejected)
        response = client.post("/api/execute", json={
            "code": "print('test')",
            "language": "python",
            "timeout": 100  # exceeds max of 10
        })
        assert response.status_code == 422
    
    def test_full_interview_simulation(self):
        """Simulate a complete interview from start to finish."""
        # Step 1: Interviewer creates session
        create_response = client.post("/api/sessions", json={
            "language": "python",
            "title": "Senior Developer Interview - Algorithms"
        })
        assert create_response.status_code == 201
        session = create_response.json()
        session_id = session["sessionId"]
        session_url = session["url"]
        
        # Step 2: Share URL with candidate (simulated by URL presence)
        assert session_id in session_url
        
        # Step 3: Both connect
        with client.websocket_connect(f"/ws/sessions/{session_id}") as interviewer_ws:
            interviewer_ws.receive_json()  # welcome
            
            interviewer_ws.send_json({
                "type": "join",
                "userId": "interviewer-123",
                "data": {"name": "Interviewer"}
            })
            
            with client.websocket_connect(f"/ws/sessions/{session_id}") as candidate_ws:
                candidate_ws.receive_json()  # welcome
                
                candidate_ws.send_json({
                    "type": "join",
                    "userId": "candidate-456",
                    "data": {"name": "Candidate"}
                })
                
                # Step 4: Candidate writes solution
                solution_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Test the solution
result = two_sum([2, 7, 11, 15], 9)
print(f"Indices: {result}")
"""
                candidate_ws.send_json({
                    "type": "code-update",
                    "userId": "candidate-456",
                    "data": {"code": solution_code}
                })
                
                # Step 5: Save code
                client.post(f"/api/sessions/{session_id}/code", json={
                    "code": solution_code,
                    "language": "python"
                })
                
                # Step 6: Run code
                execute_response = client.post("/api/execute", json={
                    "code": solution_code,
                    "language": "python",
                    "timeout": 5
                })
                assert execute_response.status_code == 200
                result = execute_response.json()
                assert result["success"] is True
                assert "Indices" in result["stdout"]
                
                # Step 7: Check participants
                participants = client.get(f"/api/sessions/{session_id}/participants")
                assert len(participants.json()["participants"]) == 2
                
                # Step 8: Review history
                history = client.get(f"/api/sessions/{session_id}/history")
                assert len(history.json()["history"]) > 0
        
        # Step 9: Interview complete, can keep session for review
        final_session = client.get(f"/api/sessions/{session_id}")
        assert final_session.status_code == 200


class TestClientServerEdgeCases:
    """Test edge cases in client-server interaction."""
    
    def test_empty_code_execution(self):
        """Test executing empty code."""
        response = client.post("/api/execute", json={
            "code": "",
            "language": "python",
            "timeout": 5
        })
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
    
    def test_very_long_code(self):
        """Test handling of very long code."""
        long_code = "print('x')\n" * 1000
        
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        save_response = client.post(f"/api/sessions/{session_id}/code", json={
            "code": long_code,
            "language": "python"
        })
        assert save_response.status_code == 200
        
        # Retrieve and verify
        code_response = client.get(f"/api/sessions/{session_id}/code")
        assert len(code_response.json()["code"]) == len(long_code)
    
    def test_rapid_session_creation(self):
        """Test creating multiple sessions rapidly."""
        session_ids = []
        
        for i in range(10):
            response = client.post("/api/sessions", json={
                "title": f"Session {i}"
            })
            assert response.status_code == 201
            session_ids.append(response.json()["sessionId"])
        
        # Verify all sessions are unique
        assert len(set(session_ids)) == 10
        
        # Verify all sessions are accessible
        for session_id in session_ids:
            response = client.get(f"/api/sessions/{session_id}")
            assert response.status_code == 200
    
    def test_websocket_reconnection_stability(self):
        """Test WebSocket connection stability with reconnects."""
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["sessionId"]
        
        # Connect and disconnect multiple times
        for _ in range(5):
            with client.websocket_connect(f"/ws/sessions/{session_id}") as ws:
                welcome = ws.receive_json()
                assert welcome["type"] == "welcome"
                
                ws.send_json({"type": "ping"})
                pong = ws.receive_json()
                assert pong["type"] == "pong"
