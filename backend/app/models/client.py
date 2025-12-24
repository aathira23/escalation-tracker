"""
Client Model
Represents companies/clients whose complaints are tracked.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    """
    Client model representing a company whose complaints are being tracked.
    
    Clients are matched to incoming emails by their email domain or
    specific contact email addresses.
    """
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    
    # Email matching: used to associate incoming complaints with clients
    email_domain = Column(String(255), nullable=True, index=True)  # e.g., "acme.com"
    contact_emails = Column(ARRAY(String), default=list)  # Specific known contacts
    
    # Business details
    industry = Column(String(100), nullable=True)
    
    # Account management
    account_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Risk tracking (updated by AI based on sentiment trends)
    risk_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account_manager = relationship("User", back_populates="managed_clients")
    escalations = relationship("Escalation", back_populates="client")
    
    def __repr__(self):
        return f"<Client {self.name}>"
