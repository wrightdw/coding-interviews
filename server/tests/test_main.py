"""Tests for the main application."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestMain:
    """Test main application endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
    
    def test_docs_available(self):
        """Test that API docs are available."""
        response = client.get("/docs")
        
        assert response.status_code == 200
    
    def test_openapi_schema(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
