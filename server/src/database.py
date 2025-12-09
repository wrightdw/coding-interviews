"""Mock database for storing sessions and code."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List
import uuid

from src.models import Language, Session, Participant, HistoryEntry


class MockDatabase:
    """In-memory mock database."""
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.code_snapshots: Dict[str, List[dict]] = {}
        self.participants: Dict[str, List[Participant]] = {}
        self.history: Dict[str, List[HistoryEntry]] = {}
    
    def create_session(
        self, 
        language: Language, 
        title: Optional[str], 
        expires_in_hours: int,
        base_url: str = "http://localhost:3000"
    ) -> Session:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(hours=expires_in_hours)
        
        session_data = {
            "sessionId": session_id,
            "title": title,
            "language": language,
            "createdAt": created_at,
            "expiresAt": expires_at,
            "activeParticipants": 0,
            "code": f"// Write your {language.value} code here\n",
        }
        
        self.sessions[session_id] = session_data
        self.code_snapshots[session_id] = []
        self.participants[session_id] = []
        self.history[session_id] = []
        
        return Session(
            **session_data,
            url=f"{base_url}/interview/{session_id}"
        )
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session_data = self.sessions.get(session_id)
        if not session_data:
            return None
        
        return Session(
            **session_data,
            url=f"http://localhost:3000/interview/{session_id}"
        )
    
    def update_session(
        self, 
        session_id: str, 
        language: Optional[Language] = None,
        title: Optional[str] = None,
        active_participants: Optional[int] = None
    ) -> Optional[Session]:
        """Update session."""
        if session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        
        if language is not None:
            session_data["language"] = language
        if title is not None:
            session_data["title"] = title
        if active_participants is not None:
            session_data["activeParticipants"] = active_participants
        
        return Session(
            **session_data,
            url=f"http://localhost:3000/interview/{session_id}"
        )
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        if session_id not in self.sessions:
            return False
        
        del self.sessions[session_id]
        self.code_snapshots.pop(session_id, None)
        self.participants.pop(session_id, None)
        self.history.pop(session_id, None)
        return True
    
    def get_code(self, session_id: str) -> Optional[dict]:
        """Get current code for session."""
        session_data = self.sessions.get(session_id)
        if not session_data:
            return None
        
        return {
            "sessionId": session_id,
            "code": session_data.get("code", ""),
            "language": session_data["language"],
            "lastModified": session_data["createdAt"]
        }
    
    def save_code(
        self, 
        session_id: str, 
        code: str, 
        language: Language,
        user_id: str = "anonymous"
    ) -> Optional[dict]:
        """Save code snapshot."""
        if session_id not in self.sessions:
            return None
        
        snapshot_id = str(uuid.uuid4())
        saved_at = datetime.now(timezone.utc)
        
        snapshot = {
            "snapshotId": snapshot_id,
            "code": code,
            "language": language,
            "savedAt": saved_at,
            "userId": user_id
        }
        
        self.code_snapshots[session_id].append(snapshot)
        self.sessions[session_id]["code"] = code
        
        # Add to history
        self.add_history_entry(
            session_id,
            user_id,
            "snapshot",
            f"Code snapshot saved",
            code
        )
        
        return {
            "sessionId": session_id,
            "snapshotId": snapshot_id,
            "savedAt": saved_at
        }
    
    def add_participant(
        self,
        session_id: str,
        user_id: str,
        name: str
    ) -> bool:
        """Add participant to session."""
        if session_id not in self.sessions:
            return False
        
        participant = Participant(
            userId=user_id,
            name=name,
            joinedAt=datetime.now(timezone.utc),
            cursorPosition=None
        )
        
        # Remove existing participant with same userId
        self.participants[session_id] = [
            p for p in self.participants[session_id] if p.userId != user_id
        ]
        
        self.participants[session_id].append(participant)
        self.sessions[session_id]["activeParticipants"] = len(
            self.participants[session_id]
        )
        
        return True
    
    def remove_participant(self, session_id: str, user_id: str) -> bool:
        """Remove participant from session."""
        if session_id not in self.sessions:
            return False
        
        self.participants[session_id] = [
            p for p in self.participants[session_id] if p.userId != user_id
        ]
        
        self.sessions[session_id]["activeParticipants"] = len(
            self.participants[session_id]
        )
        
        return True
    
    def get_participants(self, session_id: str) -> Optional[List[Participant]]:
        """Get all participants in session."""
        if session_id not in self.sessions:
            return None
        
        return self.participants.get(session_id, [])
    
    def add_history_entry(
        self,
        session_id: str,
        user_id: str,
        change_type: str,
        description: str,
        code_snapshot: Optional[str] = None
    ):
        """Add history entry."""
        if session_id not in self.sessions:
            return
        
        entry = HistoryEntry(
            timestamp=datetime.now(timezone.utc),
            userId=user_id,
            changeType=change_type,
            description=description,
            codeSnapshot=code_snapshot
        )
        
        self.history[session_id].append(entry)
    
    def get_history(
        self, 
        session_id: str, 
        limit: int = 50
    ) -> Optional[List[HistoryEntry]]:
        """Get session history."""
        if session_id not in self.sessions:
            return None
        
        history = self.history.get(session_id, [])
        return history[-limit:] if len(history) > limit else history


# Global database instance
db = MockDatabase()
