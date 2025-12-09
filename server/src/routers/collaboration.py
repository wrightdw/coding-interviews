"""Collaboration and participant routes."""

from fastapi import APIRouter, HTTPException, status, Query

from src.models import ParticipantsResponse, HistoryResponse
from src.database import db

router = APIRouter()


@router.get("/sessions/{session_id}/participants", response_model=ParticipantsResponse)
async def get_participants(session_id: str):
    """Get active participants in a session."""
    participants = db.get_participants(session_id)
    
    if participants is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return ParticipantsResponse(
        sessionId=session_id,
        participants=participants
    )


@router.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_session_history(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get session history."""
    history = db.get_history(session_id, limit=limit)
    
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return HistoryResponse(
        sessionId=session_id,
        history=history
    )
