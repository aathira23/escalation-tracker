"""
Timeline Schemas
Pydantic models for timeline event responses.
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Types of actions recorded in timeline."""
    CREATED = "created"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    STATUS_CHANGED = "status_changed"
    NOTE_ADDED = "note_added"
    PRIORITY_CHANGED = "priority_changed"
    SLA_WARNING = "sla_warning"
    SLA_BREACH = "sla_breach"
    AI_RECOMMENDATION = "ai_recommendation"


class TimelineEventResponse(BaseModel):
    """Schema for timeline event response (camelCase for frontend)."""
    id: UUID
    escalationId: UUID
    userId: Optional[UUID]
    userName: Optional[str] = None
    actionType: ActionType
    description: str
    metadata: dict
    createdAt: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_model(cls, event):
        """Convert SQLAlchemy model to response schema."""
        return cls(
            id=event.id,
            escalationId=event.escalation_id,
            userId=event.user_id,
            userName=event.user.full_name if event.user else None,
            actionType=event.action_type.value,
            description=event.description,
            metadata=event.event_metadata or {},
            createdAt=event.created_at
        )
