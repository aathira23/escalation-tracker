"""
Raw Complaint Model
Stores original email content before AI processing.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RawComplaint(Base):
    """
    Raw complaint model storing original email data.
    
    Used to:
    - Preserve original complaint text
    - Track processing status
    - Link to created escalation
    - Debug AI processing issues
    """
    __tablename__ = "raw_complaints"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Email metadata
    email_id = Column(String(500), unique=True, nullable=False, index=True)  # Message-ID header
    sender_email = Column(String(255), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    subject = Column(String(1000), nullable=True)
    body = Column(Text, nullable=False)
    
    # When the email was received (from email headers)
    received_at = Column(DateTime, nullable=False)
    
    # Processing status
    processed = Column(Boolean, default=False, index=True)
    escalation_id = Column(UUID(as_uuid=True), ForeignKey("escalations.id"), nullable=True)
    
    # Error tracking
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    escalation = relationship("Escalation", back_populates="raw_complaint")
    
    def __repr__(self):
        return f"<RawComplaint from {self.sender_email}, processed={self.processed}>"
