"""
User Model
Represents system users with roles: admin, manager, viewer
Viewers become resolvers when assigned an escalation.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from app.models.association import project_users, user_skills


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and authorization.
    
    Roles:
    - admin: Full system access, can do everything
    - manager: Oversees escalations, approves assignments, views analytics
    - viewer: Read-only visibility + internal notes; becomes resolver when assigned
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    
    # Expertise tags for AI assignment recommendations
    expertise_tags = Column(ARRAY(String), default=list)
    
    # Workload management
    max_concurrent_escalations = Column(Integer, default=5)
    current_escalation_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_escalations = relationship(
        "Escalation",
        back_populates="assignee",
        foreign_keys="Escalation.assigned_to"
    )
    created_escalations = relationship(
        "Escalation",
        back_populates="creator",
        foreign_keys="Escalation.created_by"
    )
    managed_clients = relationship("Client", back_populates="account_manager")
    timeline_events = relationship("TimelineEvent", back_populates="user")
    notes = relationship("Note", back_populates="author")
    
    # New relationships for project/department support
    projects = relationship("Project", secondary="project_users", back_populates="members")
    skills = relationship("Skill", secondary="user_skills", back_populates="users")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
