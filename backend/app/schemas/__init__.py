"""
Pydantic Schemas Package
"""
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, Token, TokenData
)
from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse
)
from app.schemas.escalation import (
    EscalationCreate, EscalationUpdate, EscalationResponse,
    EscalationAssign, EscalationStatusUpdate
)
from app.schemas.timeline import TimelineEventResponse
from app.schemas.note import NoteCreate, NoteResponse
from app.schemas.analytics import (
    DashboardStats, ClientAnalytics, TeamAnalytics
)

__all__ = [
    # User
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "Token", "TokenData",
    # Client
    "ClientCreate", "ClientUpdate", "ClientResponse",
    # Escalation
    "EscalationCreate", "EscalationUpdate", "EscalationResponse",
    "EscalationAssign", "EscalationStatusUpdate",
    # Timeline
    "TimelineEventResponse",
    # Note
    "NoteCreate", "NoteResponse",
    # Analytics
    "DashboardStats", "ClientAnalytics", "TeamAnalytics"
]
