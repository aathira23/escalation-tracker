"""
Notes Router
Handles internal notes for escalations.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.escalation_service import EscalationService
from app.schemas.note import NoteCreate, NoteResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/escalations/{escalation_id}/notes", tags=["Notes"])


@router.get("", response_model=list[NoteResponse])
async def list_notes(
    escalation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all internal notes for an escalation.
    All authenticated users can view notes.
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    notes = EscalationService.get_notes(db, escalation_id)
    return [NoteResponse.from_orm_model(n) for n in notes]


@router.post("", response_model=NoteResponse)
async def create_note(
    escalation_id: UUID,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an internal note to an escalation.
    All authenticated users can add notes.
    """
    escalation = EscalationService.get_escalation_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    note = EscalationService.add_note(
        db,
        escalation_id,
        current_user.id,
        note_data.content
    )
    
    return NoteResponse.from_orm_model(note)
