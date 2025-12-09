"""Session management routes."""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from src.models import (
    Session,
    SessionCreate,
    SessionUpdate,
    CodeResponse,
    CodeSave,
    CodeSaveResponse,
)
from src.database import db

router = APIRouter()


@router.post("/sessions", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(session_data: Optional[SessionCreate] = None):
    """Create a new interview session."""
    if session_data is None:
        session_data = SessionCreate()
    
    session = db.create_session(
        language=session_data.language,
        title=session_data.title,
        expires_in_hours=session_data.expiresIn
    )
    
    return session


@router.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get session details."""
    session = db.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.patch("/sessions/{session_id}", response_model=Session)
async def update_session(session_id: str, update_data: SessionUpdate):
    """Update session settings."""
    session = db.update_session(
        session_id=session_id,
        language=update_data.language,
        title=update_data.title
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """Delete a session."""
    success = db.delete_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.get("/sessions/{session_id}/code", response_model=CodeResponse)
async def get_code(session_id: str):
    """Get current code for a session."""
    code_data = db.get_code(session_id)
    
    if not code_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return CodeResponse(**code_data)


@router.post("/sessions/{session_id}/code", response_model=CodeSaveResponse)
async def save_code(session_id: str, code_data: CodeSave):
    """Save a code snapshot."""
    result = db.save_code(
        session_id=session_id,
        code=code_data.code,
        language=code_data.language
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return CodeSaveResponse(**result)
