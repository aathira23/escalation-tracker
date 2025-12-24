"""
Escalation Model
Core entity representing a client complaint/escalation.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class EscalationPriority(str, enum.Enum):
    """Priority levels for escalations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EscalationStatus(str, enum.Enum):
    """Status workflow: open -> in_progress -> resolved"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class Escalation(Base):
    """
    Escalation model representing a formal complaint record.
    
    Lifecycle:
    1. Created from AI processing of raw email complaint
    2. Visible to all users
    3. Manager assigns to a viewer (who becomes resolver)
    4. Resolver updates status: open -> in_progress -> resolved
    5. SLA tracked with 60-day window from creation
    """
    __tablename__ = "escalations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core information (populated by AI)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=True)
    
    # Client reference
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    # Classification (AI-generated)
    priority = Column(SQLEnum(EscalationPriority), default=EscalationPriority.MEDIUM)
    status = Column(SQLEnum(EscalationStatus), default=EscalationStatus.OPEN)
    complaint_type = Column(String(100), nullable=True)
    
    # Sentiment analysis (AI-generated)
    sentiment_score = Column(Float, default=0.0)  # -1.0 (very negative) to 1.0 (positive)
    churn_risk = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # AI assignment recommendation (stored for manager review)
    ai_recommended_assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ai_assignment_reason = Column(Text, nullable=True)
    ai_assignment_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # SLA tracking
    due_date = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="escalations")
    assignee = relationship(
        "User",
        back_populates="assigned_escalations",
        foreign_keys=[assigned_to]
    )
    creator = relationship(
        "User",
        back_populates="created_escalations",
        foreign_keys=[created_by]
    )
    ai_recommended_assignee = relationship(
        "User",
        foreign_keys=[ai_recommended_assignee_id]
    )
    project = relationship("Project", back_populates="escalations")
    timeline_events = relationship("TimelineEvent", back_populates="escalation", order_by="TimelineEvent.created_at")
    notes = relationship("Note", back_populates="escalation", order_by="Note.created_at.desc()")
    raw_complaint = relationship("RawComplaint", back_populates="escalation", uselist=False)
    
    def __init__(self, **kwargs):
        """Set default due_date to 60 days from now if not provided."""
        if 'due_date' not in kwargs:
            kwargs['due_date'] = datetime.utcnow() + timedelta(days=60)
        super().__init__(**kwargs)
    
    @property
    def days_until_due(self) -> int:
        """Calculate days remaining until due date."""
        if self.resolved_at:
            return 0
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_overdue(self) -> bool:
        """Check if escalation is past due date and not resolved."""
        if self.resolved_at:
            return False
        return datetime.utcnow() > self.due_date
    
    def __repr__(self):
        return f"<Escalation {self.title[:50]}... ({self.status.value})>"
