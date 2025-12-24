"""
Project Model
Represents specific projects or teams within a department.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.association import project_users


class Project(Base):
    """
    Project model representing a team or specific area of work within a department.
    Escalations are assigned to projects.
    """
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="projects")
    members = relationship("User", secondary="project_users", back_populates="projects")
    escalations = relationship("Escalation", back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.name}>"
