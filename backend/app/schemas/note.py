"""
Note Schemas
Pydantic models for note-related API operations.
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# Request schemas

class NoteCreate(BaseModel):
    """Schema for creating a new internal note."""
    content: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    content: str = Field(..., min_length=1)


# Response schemas

class NoteResponse(BaseModel):
    """Schema for note response (camelCase for frontend)."""
    id: UUID
    escalationId: UUID
    authorId: UUID
    authorName: Optional[str] = None
    content: str
    isInternal: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_model(cls, note):
        """Convert SQLAlchemy model to response schema."""
        return cls(
            id=note.id,
            escalationId=note.escalation_id,
            authorId=note.author_id,
            authorName=note.author.full_name if note.author else None,
            content=note.content,
            isInternal=note.is_internal,
            createdAt=note.created_at,
            updatedAt=note.updated_at
        )
