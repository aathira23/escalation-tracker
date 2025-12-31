"""
User Schemas
Pydantic models for user-related API operations.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration for API."""
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


# Request schemas

class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """Schema for creating a new user (admin only)."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.VIEWER
    max_concurrent_escalations: int = Field(default=5, ge=1, le=20)
    department_id: Optional[UUID] = None
    expertise_tags: Optional[List[str]] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Schema for updating user details."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    expertise_tags: Optional[List[str]] = None
    max_concurrent_escalations: Optional[int] = Field(None, ge=1, le=20)
    is_active: Optional[bool] = None
    department_id: Optional[UUID] = None
    project_ids: Optional[List[UUID]] = None


# Response schemas

class UserResponse(BaseModel):
    """Schema for user response (camelCase for frontend)."""
    id: UUID
    email: str
    fullName: str
    role: UserRole
    expertiseTags: List[str]
    maxConcurrentEscalations: int
    currentEscalationCount: int
    isActive: bool
    departmentId: Optional[UUID] = None
    departmentName: Optional[str] = None
    projectIds: List[UUID] = []
    projectNames: List[str] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, user):
        """Convert SQLAlchemy model to response schema."""
        return cls(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            expertiseTags=user.expertise_tags or [],
            maxConcurrentEscalations=user.max_concurrent_escalations,
            currentEscalationCount=user.current_escalation_count,
            isActive=user.is_active,
            departmentId=user.department_id,
            departmentName=user.department.name if user.department else None,
            projectIds=[p.id for p in user.projects],
            projectNames=[p.name for p in user.projects],
            createdAt=user.created_at,
            updatedAt=user.updated_at
        )


# Token schemas

class Token(BaseModel):
    """Schema for JWT token response."""
    accessToken: str
    tokenType: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[str] = None
