"""
AI Suggestion Model
Stores AI-generated suggestions for assignments and resolutions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class AISuggestion(Base):
    """
    AI Suggestion model for storing moderator suggestions and resolution tips.
    """
    __tablename__ = "ai_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escalation_id = Column(UUID(as_uuid=True), ForeignKey("escalations.id"), nullable=False)
    
    # Type of suggestion: "assignment" or "resolution"
    suggestion_type = Column(String(50), nullable=False)
    
    # The actual content (JSON or Text)
    content = Column(JSON, nullable=False)
    
    # Metadata
    confidence_score = Column(Float, nullable=True)
    model_version = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    escalation = relationship("Escalation", backref="ai_suggestions")
    
    def __repr__(self):
        return f"<AISuggestion {self.suggestion_type} for {self.escalation_id}>"
