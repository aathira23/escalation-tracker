"""
Escalations Router
Handles escalation management endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.database import get_db
from app.services.escalation_service import EscalationService
from app.schemas.escalation import (
    EscalationCreate, EscalationUpdate, EscalationResponse,
    EscalationAssign, EscalationStatusUpdate, EscalationListResponse
)
from app.schemas.timeline import TimelineEventResponse
from app.dependencies import get_current_user, require_manager_or_admin
from app.models.escalation import Escalation, EscalationStatus, EscalationPriority
from app.models.timeline import ActionType
from app.models.client import Client
from app.models.user import User, UserRole
from app.core.websocket import manager

router = APIRouter(prefix="/api/escalations", tags=["Escalations"])


@router.get("", response_model=EscalationListResponse)
async def list_escalations(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    client_id: Optional[UUID] = Query(None, description="Filter by client"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assignee"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all escalations with optional filters.
    All authenticated users can view all escalations (transparency principle).
    """
    # Convert string filters to enums
    status_enum = None
    if status:
        try:
            status_enum = EscalationStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    priority_enum = None
    if priority:
        try:
            priority_enum = EscalationPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
    
    escalations, total = EscalationService.get_all_escalations(
        db,
        status=status_enum,
        priority=priority_enum,
        client_id=client_id,
        assigned_to=assigned_to,
        page=page,
        page_size=page_size
    )
    
    return EscalationListResponse(
        items=[EscalationResponse.from_orm_model(e) for e in escalations],
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.post("", response_model=EscalationResponse)
async def create_escalation(
    escalation_data: EscalationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Create a new escalation (managers and admins only).
    Usually created automatically by AI from email ingestion.
    """
    # Verify client exists
    client = db.query(Client).filter(Client.id == escalation_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    escalation = EscalationService.create_escalation(
        db,
        title=escalation_data.title,
        description=escalation_data.description,
        client_id=escalation_data.client_id,
        created_by=current_user.id,
        executive_summary=escalation_data.executive_summary,
        priority=EscalationPriority(escalation_data.priority.value),
        complaint_type=escalation_data.complaint_type,
        sentiment_score=escalation_data.sentiment_score,
        churn_risk=escalation_data.churn_risk
    )
    
    return EscalationResponse.from_orm_model(escalation)


@router.get("/{escalation_id}", response_model=EscalationResponse)
async def get_escalation(
    escalation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get escalation by ID.
    All authenticated users can view any escalation.
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    return EscalationResponse.from_orm_model(escalation)


@router.put("/{escalation_id}", response_model=EscalationResponse)
async def update_escalation(
    escalation_id: UUID,
    escalation_data: EscalationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Update escalation details (managers and admins only).
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    # Apply updates
    if escalation_data.title:
        escalation.title = escalation_data.title
    if escalation_data.description:
        escalation.description = escalation_data.description
    if escalation_data.executive_summary is not None:
        escalation.executive_summary = escalation_data.executive_summary
    if escalation_data.priority:
        old_priority = escalation.priority
        escalation.priority = EscalationPriority(escalation_data.priority.value)
        if old_priority != escalation.priority:
            EscalationService._add_timeline_event(
                db, escalation_id, current_user.id,
                ActionType.PRIORITY_CHANGED,
                f"Priority changed: {old_priority.value} → {escalation.priority.value}",
                {"old": old_priority.value, "new": escalation.priority.value}
            )
    if escalation_data.complaint_type is not None:
        escalation.complaint_type = escalation_data.complaint_type
    
    db.commit()
    db.refresh(escalation)
    
    return EscalationResponse.from_orm_model(escalation)


@router.post("/{escalation_id}/assign", response_model=EscalationResponse)
async def assign_escalation(
    escalation_id: UUID,
    assignment: EscalationAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Assign escalation to a resolver (managers and admins only).
    Viewer becomes resolver when assigned an escalation.
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    # Verify assignee exists and is a viewer
    assignee = db.query(User).filter(User.id == assignment.assignee_id).first()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found"
        )
    
    if assignee.role != UserRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only assign escalations to viewers"
        )
    
    # Manager permission check: Must be in the same project/department as the escalation
    if current_user.role == UserRole.MANAGER:
        # Check if manager is in the project
        if escalation.project_id:
            manager_in_project = db.query(User).join(User.projects).filter(
                User.id == current_user.id,
                Project.id == escalation.project_id
            ).first()
            if not manager_in_project:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only assign escalations in their own projects"
                )
    
    # Check capacity
    if assignee.current_escalation_count >= assignee.max_concurrent_escalations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assignee is at maximum capacity ({assignee.max_concurrent_escalations} escalations)"
        )
    
    try:
        escalation = EscalationService.assign_escalation(
            db,
            escalation_id,
            assignment.assignee_id,
            current_user.id,
            assignment.reason
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Broadcast update
    await manager.broadcast({
        "type": "escalation_assigned",
        "escalation_id": str(escalation.id),
        "assignee_id": str(assignment.assignee_id),
        "assignee_name": assignee.full_name,
        "assigned_by_name": current_user.full_name
    })

    return EscalationResponse.from_orm_model(escalation)


@router.put("/{escalation_id}/status", response_model=EscalationResponse)
async def update_escalation_status(
    escalation_id: UUID,
    status_update: EscalationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update escalation status.
    Resolvers (assigned viewers), managers, and admins can update status.
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    # Permission check: resolver, manager, or admin
    is_resolver = escalation.assigned_to == current_user.id
    is_manager_or_admin = current_user.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    if not is_resolver and not is_manager_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned resolver, managers, or admins can update status"
        )
    
    try:
        escalation = EscalationService.update_status(
            db,
            escalation_id,
            EscalationStatus(status_update.status.value),
            current_user.id,
            status_update.note
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Broadcast update
    await manager.broadcast({
        "type": "escalation_status_updated",
        "escalation_id": str(escalation.id),
        "status": escalation.status.value,
        "updated_by_name": current_user.full_name
    })

    return EscalationResponse.from_orm_model(escalation)


@router.get("/{escalation_id}/timeline", response_model=list[TimelineEventResponse])
async def get_escalation_timeline(
    escalation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get timeline of events for an escalation.
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    events = EscalationService.get_timeline(db, escalation_id)
    return [TimelineEventResponse.from_orm_model(e) for e in events]
