"""
Note Model
Internal notes attached to escalations.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Note(Base):
    """
    Note model for internal comments on escalations.
    
    All notes are internal (not client-facing) and are used
    for team communication during escalation resolution.
    """
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    escalation_id = Column(UUID(as_uuid=True), ForeignKey("escalations.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    
    # All notes are internal by design (no client communication)
    is_internal = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    escalation = relationship("Escalation", back_populates="notes")
    author = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Note by {self.author_id} on {self.escalation_id}>"
