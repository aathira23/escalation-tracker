"""
Skill Model
Represents skills or expertise tags that can be assigned to users.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.association import user_skills


class Skill(Base):
    """
    Skill model representing an expertise area (e.g., "Python", "Billing").
    """
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-Many Relationship with Users (handled via implicit table or association)
    # For simplicity, we'll keep it one-to-many or use the existing list on User,
    # BUT user requested "skills (linked to users)". 
    # Let's create a UserSkill association or just many-to-many.
    users = relationship("User", secondary="user_skills", back_populates="skills")
    
    def __repr__(self):
        return f"<Skill {self.name}>"
