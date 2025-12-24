"""
Timeline Event Model
Records all actions taken on an escalation for audit trail.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ActionType(str, enum.Enum):
    """Types of actions that can be recorded in timeline."""
    CREATED = "created"
    ASSIGNED = "assigned"
    REASSIGNED = "reassigned"
    STATUS_CHANGED = "status_changed"
    NOTE_ADDED = "note_added"
    PRIORITY_CHANGED = "priority_changed"
    SLA_WARNING = "sla_warning"
    SLA_BREACH = "sla_breach"
    AI_RECOMMENDATION = "ai_recommendation"


class TimelineEvent(Base):
    """
    Timeline event model for tracking all actions on escalations.
    
    Provides full audit trail with:
    - What action was taken
    - Who took the action
    - When it happened
    - Additional metadata (e.g., old/new values for changes)
    """
    __tablename__ = "timeline_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    escalation_id = Column(UUID(as_uuid=True), ForeignKey("escalations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for system events
    
    # Event details
    action_type = Column(SQLEnum(ActionType), nullable=False)
    description = Column(Text, nullable=False)
    
    # Flexible metadata storage (e.g., {"old_status": "open", "new_status": "in_progress"})
    event_metadata = Column(JSONB, default=dict)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    escalation = relationship("Escalation", back_populates="timeline_events")
    user = relationship("User", back_populates="timeline_events")
    
    def __repr__(self):
        return f"<TimelineEvent {self.action_type.value} on {self.escalation_id}>"
