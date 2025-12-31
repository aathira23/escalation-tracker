"""
Client Schemas
Pydantic models for client-related API operations.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# Request schemas

class ClientCreate(BaseModel):
    """Schema for creating a new client."""
    name: str = Field(..., min_length=1, max_length=255)
    email_domain: Optional[str] = Field(None, max_length=255)
    contact_emails: List[EmailStr] = []
    industry: Optional[str] = Field(None, max_length=100)
    account_manager_id: Optional[UUID] = None


class ClientUpdate(BaseModel):
    """Schema for updating client details."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email_domain: Optional[str] = Field(None, max_length=255)
    contact_emails: Optional[List[EmailStr]] = None
    industry: Optional[str] = Field(None, max_length=100)
    account_manager_id: Optional[UUID] = None


# Response schemas

class ClientResponse(BaseModel):
    """Schema for client response (camelCase for frontend)."""
    id: UUID
    name: str
    emailDomain: Optional[str]
    contactEmails: List[str]
    industry: Optional[str]
    accountManagerId: Optional[UUID]
    riskScore: float
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_model(cls, client):
        """Convert SQLAlchemy model to response schema."""
        return cls(
            id=client.id,
            name=client.name,
            emailDomain=client.email_domain,
            contactEmails=client.contact_emails or [],
            industry=client.industry,
            accountManagerId=client.account_manager_id,
            riskScore=client.risk_score,
            createdAt=client.created_at,
            updatedAt=client.updated_at
        )
