"""Pydantic models for request/response validation."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class Language(str, Enum):
    """Supported programming languages."""
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"


class SessionCreate(BaseModel):
    """Request model for creating a session."""
    language: Language = Language.JAVASCRIPT
    title: Optional[str] = None
    expiresIn: int = Field(default=24, ge=1, le=168)  # 1-168 hours


class SessionUpdate(BaseModel):
    """Request model for updating a session."""
    language: Optional[Language] = None
    title: Optional[str] = None


class Session(BaseModel):
    """Response model for session."""
    sessionId: str
    title: Optional[str] = None
    language: Language
    createdAt: datetime
    expiresAt: datetime
    activeParticipants: int = 0
    url: str


class CodeSave(BaseModel):
    """Request model for saving code."""
    code: str
    language: Language


class CodeResponse(BaseModel):
    """Response model for code retrieval."""
    sessionId: str
    code: str
    language: Language
    lastModified: datetime


class CodeSaveResponse(BaseModel):
    """Response model for code save."""
    sessionId: str
    snapshotId: str
    savedAt: datetime


class ExecuteRequest(BaseModel):
    """Request model for code execution."""
    code: str
    language: Language
    stdin: str = ""
    timeout: int = Field(default=5, ge=1, le=10)


class ExecutionResult(BaseModel):
    """Response model for code execution."""
    success: bool
    stdout: str
    stderr: str
    exitCode: int
    executionTime: float
    error: Optional[str] = None


class Participant(BaseModel):
    """Model for session participant."""
    userId: str
    name: str
    joinedAt: datetime
    cursorPosition: Optional[dict] = None


class ParticipantsResponse(BaseModel):
    """Response model for participants list."""
    sessionId: str
    participants: List[Participant]


class HistoryEntry(BaseModel):
    """Model for history entry."""
    timestamp: datetime
    userId: str
    changeType: str
    description: str
    codeSnapshot: Optional[str] = None


class HistoryResponse(BaseModel):
    """Response model for session history."""
    sessionId: str
    history: List[HistoryEntry]


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    statusCode: int
