"""
Escalation Schemas
Pydantic models for escalation-related API operations.
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class EscalationPriority(str, Enum):
    """Priority levels for escalations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EscalationStatus(str, Enum):
    """Status workflow: open -> in_progress -> resolved"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


# Request schemas

class EscalationCreate(BaseModel):
    """Schema for creating a new escalation (usually from AI processing)."""
    title: str = Field(..., min_length=1, max_length=500)
    description: str
    executive_summary: Optional[str] = None
    client_id: UUID
    priority: EscalationPriority = EscalationPriority.MEDIUM
    complaint_type: Optional[str] = None
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    churn_risk: float = Field(default=0.0, ge=0.0, le=1.0)


class EscalationUpdate(BaseModel):
    """Schema for updating escalation details."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    executive_summary: Optional[str] = None
    priority: Optional[EscalationPriority] = None
    complaint_type: Optional[str] = None


class EscalationAssign(BaseModel):
    """Schema for assigning escalation to a resolver (manager action)."""
    assignee_id: UUID
    reason: Optional[str] = None


class EscalationStatusUpdate(BaseModel):
    """Schema for updating escalation status (resolver action)."""
    status: EscalationStatus
    note: Optional[str] = None  # Optional note about the status change


class AISuggestionResponse(BaseModel):
    """Schema for AI suggestion response."""
    id: UUID
    suggestionType: str
    content: dict
    confidenceScore: Optional[float]
    modelVersion: Optional[str]
    createdAt: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, suggestion):
        return cls(
            id=suggestion.id,
            suggestionType=suggestion.suggestion_type,
            content=suggestion.content,
            confidenceScore=suggestion.confidence_score,
            modelVersion=suggestion.model_version,
            createdAt=suggestion.created_at
        )


# Response schemas

class EscalationResponse(BaseModel):
    """Schema for escalation response (camelCase for frontend)."""
    id: UUID
    title: str
    description: str
    executiveSummary: Optional[str]
    clientId: UUID
    clientName: Optional[str] = None
    priority: EscalationPriority
    status: EscalationStatus
    complaintType: Optional[str]
    sentimentScore: float
    churnRisk: float
    assignedTo: Optional[UUID]
    assigneeName: Optional[str] = None
    createdBy: UUID
    creatorName: Optional[str] = None
    projectId: Optional[UUID] = None
    projectName: Optional[str] = None
    departmentName: Optional[str] = None
    aiRecommendedAssigneeId: Optional[UUID]
    aiAssignmentReason: Optional[str]
    aiAssignmentConfidence: Optional[float]
    aiSuggestions: Optional[list[AISuggestionResponse]] = None
    dueDate: datetime
    resolvedAt: Optional[datetime]
    daysUntilDue: int
    isOverdue: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_model(cls, escalation, include_names: bool = True):
        """Convert SQLAlchemy model to response schema."""
        return cls(
            id=escalation.id,
            title=escalation.title,
            description=escalation.description,
            executiveSummary=escalation.executive_summary,
            clientId=escalation.client_id,
            clientName=escalation.client.name if include_names and escalation.client else None,
            priority=escalation.priority.value,
            status=escalation.status.value,
            complaintType=escalation.complaint_type,
            sentimentScore=escalation.sentiment_score,
            churnRisk=escalation.churn_risk,
            assignedTo=escalation.assigned_to,
            assigneeName=escalation.assignee.full_name if include_names and escalation.assignee else None,
            createdBy=escalation.created_by,
            creatorName=escalation.creator.full_name if include_names and escalation.creator else None,
            projectId=escalation.project_id,
            projectName=escalation.project.name if include_names and escalation.project else None,
            departmentName=escalation.project.department.name if include_names and escalation.project and escalation.project.department else None,
            aiRecommendedAssigneeId=escalation.ai_recommended_assignee_id,
            aiAssignmentReason=escalation.ai_assignment_reason,
            aiAssignmentConfidence=escalation.ai_assignment_confidence,
            aiSuggestions=[AISuggestionResponse.from_orm_model(s) for s in escalation.ai_suggestions] if hasattr(escalation, 'ai_suggestions') and escalation.ai_suggestions else [],
            dueDate=escalation.due_date,
            resolvedAt=escalation.resolved_at,
            daysUntilDue=escalation.days_until_due,
            isOverdue=escalation.is_overdue,
            createdAt=escalation.created_at,
            updatedAt=escalation.updated_at
        )


class EscalationListResponse(BaseModel):
    """Schema for paginated escalation list."""
    items: list[EscalationResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int
