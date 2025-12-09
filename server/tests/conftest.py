"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database import db


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    db.sessions.clear()
    db.code_snapshots.clear()
    db.participants.clear()
    db.history.clear()
    yield
    db.sessions.clear()
    db.code_snapshots.clear()
    db.participants.clear()
    db.history.clear()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_session(client):
    """Create a sample session for testing."""
    response = client.post("/api/sessions", json={
        "language": "javascript",
        "title": "Test Session"
    })
    return response.json()
