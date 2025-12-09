"""Tests for code execution endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestExecution:
    """Test code execution endpoints."""
    
    def test_execute_python_success(self):
        """Test successful Python code execution."""
        payload = {
            "code": "print('Hello from Python')",
            "language": "python",
            "timeout": 5
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "Hello from Python" in data["stdout"]
        assert data["exitCode"] == 0
        assert data["executionTime"] >= 0
    
    def test_execute_python_with_error(self):
        """Test Python code execution with error."""
        payload = {
            "code": "print(undefined_variable)",
            "language": "python",
            "timeout": 5
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert data["exitCode"] == 1
        assert data["error"] is not None
    
    def test_execute_python_with_math(self):
        """Test Python code with calculations."""
        payload = {
            "code": "result = sum(range(1, 11))\nprint(f'Sum: {result}')",
            "language": "python",
            "timeout": 5
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "Sum: 55" in data["stdout"]
    
    def test_execute_javascript_mock(self):
        """Test JavaScript execution (mock response)."""
        payload = {
            "code": "console.log('Hello')",
            "language": "javascript",
            "timeout": 5
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # JavaScript execution not fully implemented in mock
        assert "error" in data or "stderr" in data
    
    def test_execute_java_mock(self):
        """Test Java execution (mock response)."""
        payload = {
            "code": "public class Main { public static void main(String[] args) {} }",
            "language": "java",
            "timeout": 5
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Java execution not fully implemented in mock
        assert "error" in data or "stderr" in data
    
    def test_execute_cpp_mock(self):
        """Test C++ execution (mock response)."""
        payload = {
            "code": "#include <iostream>\nint main() { return 0; }",
            "language": "cpp",
            "timeout": 5
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # C++ execution not fully implemented in mock
        assert "error" in data or "stderr" in data
    
    def test_execute_invalid_language(self):
        """Test execution with invalid language."""
        payload = {
            "code": "print('test')",
            "language": "invalid",
            "timeout": 5
        }
        
        # This should fail validation at the Pydantic level
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_execute_timeout_validation(self):
        """Test execution with invalid timeout."""
        payload = {
            "code": "print('test')",
            "language": "python",
            "timeout": 15  # Max is 10
        }
        
        response = client.post("/api/execute", json=payload)
        
        assert response.status_code == 422  # Validation error
