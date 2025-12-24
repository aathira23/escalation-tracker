"""
Escalation Service
Business logic for escalation management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.escalation import Escalation, EscalationStatus, EscalationPriority
from app.models.timeline import TimelineEvent, ActionType
from app.models.note import Note
from app.models.client import Client
from app.models.user import User, UserRole
from app.models.project import Project
from app.core.websocket import manager


class EscalationService:
    """Service for escalation operations."""
    
    @staticmethod
    def create_escalation(
        db: Session,
        title: str,
        description: str,
        client_id: UUID,
        created_by: UUID,
        project_id: Optional[UUID] = None,
        executive_summary: Optional[str] = None,
        priority: EscalationPriority = EscalationPriority.MEDIUM,
        complaint_type: Optional[str] = None,
        sentiment_score: float = 0.0,
        churn_risk: float = 0.0
    ) -> Escalation:
        """Create a new escalation."""
        escalation = Escalation(
            title=title,
            description=description,
            executive_summary=executive_summary,
            client_id=client_id,
            project_id=project_id,
            priority=priority,
            complaint_type=complaint_type,
            sentiment_score=sentiment_score,
            churn_risk=churn_risk,
            created_by=created_by
        )
        db.add(escalation)
        db.commit()
        db.refresh(escalation)
        
        # Create timeline event
        EscalationService._add_timeline_event(
            db,
            escalation.id,
            created_by,
            ActionType.CREATED,
            f"Escalation created with priority: {priority.value}"
        )
        
        return escalation
    
    @staticmethod
    def get_escalation_by_id(db: Session, escalation_id: UUID) -> Optional[Escalation]:
        """Get an escalation by ID."""
        return db.query(Escalation).filter(Escalation.id == escalation_id).first()
    
    @staticmethod
    def get_all_escalations(
        db: Session,
        status: Optional[EscalationStatus] = None,
        priority: Optional[EscalationPriority] = None,
        client_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[Escalation], int]:
        """Get escalations with optional filters and pagination."""
        query = db.query(Escalation)
        
        if status:
            query = query.filter(Escalation.status == status)
        if priority:
            query = query.filter(Escalation.priority == priority)
        if client_id:
            query = query.filter(Escalation.client_id == client_id)
        if assigned_to:
            query = query.filter(Escalation.assigned_to == assigned_to)
        
        total = query.count()
        
        escalations = query.order_by(Escalation.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        
        return escalations, total
    
    @staticmethod
    def assign_escalation(
        db: Session,
        escalation_id: UUID,
        assignee_id: UUID,
        assigned_by: UUID,
        reason: Optional[str] = None
    ) -> Escalation:
        """Assign an escalation to a resolver (viewer becomes resolver)."""
        escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if not escalation:
            raise ValueError("Escalation not found")
        
        # Verify project team restriction
        if escalation.project_id:
            # Check if assignee is in the project
            # Using the relationship members
            is_member = db.query(User).join(User.projects).filter(
                User.id == assignee_id,
                Project.id == escalation.project_id
            ).first()
            if not is_member:
                raise ValueError("Assignee must be a member of the escalation's project")

        old_assignee_id = escalation.assigned_to
        
        # Update assignee's escalation count
        if old_assignee_id:
            old_assignee = db.query(User).filter(User.id == old_assignee_id).first()
            if old_assignee:
                old_assignee.current_escalation_count = max(0, old_assignee.current_escalation_count - 1)
        
        new_assignee = db.query(User).filter(User.id == assignee_id).first()
        if new_assignee:
            new_assignee.current_escalation_count += 1
        
        escalation.assigned_to = assignee_id
        
        # Update status to in_progress if currently open
        if escalation.status == EscalationStatus.OPEN:
            escalation.status = EscalationStatus.IN_PROGRESS
        
        db.commit()
        db.refresh(escalation)
        
        # Record timeline event
        action_type = ActionType.REASSIGNED if old_assignee_id else ActionType.ASSIGNED
        description = f"Assigned to {new_assignee.full_name if new_assignee else 'unknown'}"
        if reason:
            description += f". Reason: {reason}"
        
        EscalationService._add_timeline_event(
            db,
            escalation_id,
            assigned_by,
            action_type,
            description,
            {"assignee_id": str(assignee_id), "previous_assignee_id": str(old_assignee_id) if old_assignee_id else None}
        )
        
        return escalation
    
    @staticmethod
    def update_status(
        db: Session,
        escalation_id: UUID,
        new_status: EscalationStatus,
        updated_by: UUID,
        note: Optional[str] = None
    ) -> Escalation:
        """Update escalation status."""
        escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if not escalation:
            raise ValueError("Escalation not found")
        
        old_status = escalation.status
        escalation.status = new_status
        
        if new_status == EscalationStatus.RESOLVED:
            escalation.resolved_at = datetime.utcnow()
            # Decrement resolver's count
            if escalation.assigned_to:
                assignee = db.query(User).filter(User.id == escalation.assigned_to).first()
                if assignee:
                    assignee.current_escalation_count = max(0, assignee.current_escalation_count - 1)
        
        db.commit()
        db.refresh(escalation)
        
        # Record timeline event
        description = f"Status changed: {old_status.value} → {new_status.value}"
        if note:
            description += f". Note: {note}"
        
        EscalationService._add_timeline_event(
            db,
            escalation_id,
            updated_by,
            ActionType.STATUS_CHANGED,
            description,
            {"old_status": old_status.value, "new_status": new_status.value}
        )
        
        return escalation
    
    @staticmethod
    def add_note(
        db: Session,
        escalation_id: UUID,
        author_id: UUID,
        content: str
    ) -> Note:
        """Add an internal note to an escalation."""
        note = Note(
            escalation_id=escalation_id,
            author_id=author_id,
            content=content
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        # Record timeline event
        EscalationService._add_timeline_event(
            db,
            escalation_id,
            author_id,
            ActionType.NOTE_ADDED,
            "Internal note added"
        )
        
        return note
    
    @staticmethod
    def get_notes(db: Session, escalation_id: UUID) -> list[Note]:
        """Get all notes for an escalation."""
        return db.query(Note).filter(Note.escalation_id == escalation_id) \
            .order_by(Note.created_at.desc()).all()
    
    @staticmethod
    def get_timeline(db: Session, escalation_id: UUID) -> list[TimelineEvent]:
        """Get timeline events for an escalation."""
        return db.query(TimelineEvent).filter(TimelineEvent.escalation_id == escalation_id) \
            .order_by(TimelineEvent.created_at.asc()).all()
    
    @staticmethod
    def store_ai_resolution_suggestions(
        db: Session,
        escalation_id: UUID,
        suggestions: list[str]
    ) -> None:
        """
        Store AI-generated resolution suggestions in the ai_suggestions table.
        """
        if not suggestions:
            return
            
        from app.models.ai_suggestion import AISuggestion
        
        suggestion = AISuggestion(
            escalation_id=escalation_id,
            suggestion_type="resolution",
            content={
                "steps": suggestions
            },
            confidence_score=0.8  # Default confidence for extraction
        )
        db.add(suggestion)
        db.commit()

    @staticmethod
    def set_ai_recommendation(
        db: Session,
        escalation_id: UUID,
        recommended_assignee_id: UUID,
        reason: str,
        confidence: float
    ) -> Escalation:
        """Set AI assignment recommendation for manager review."""
        escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if not escalation:
            raise ValueError("Escalation not found")
        
        escalation.ai_recommended_assignee_id = recommended_assignee_id
        escalation.ai_assignment_reason = reason
        escalation.ai_assignment_confidence = confidence
        
        db.commit()
        db.refresh(escalation)
        
        # Record timeline event
        assignee = db.query(User).filter(User.id == recommended_assignee_id).first()
        EscalationService._add_timeline_event(
            db,
            escalation_id,
            None,  # System event
            ActionType.AI_RECOMMENDATION,
            f"AI recommends: {assignee.full_name if assignee else 'unknown'} (confidence: {confidence:.0%})",
            {"recommended_id": str(recommended_assignee_id), "reason": reason, "confidence": confidence}
        )
        
        return escalation
    
    @staticmethod
    def get_suggested_moderators(
        db: Session,
        escalation_id: UUID
    ) -> list[dict]:
        """
        Get suggested moderators for an escalation based on skills and workload.
        """
        from app.agents.assignment_agent import AssignmentAgent
        
        escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if not escalation:
            return []
            
        # Find users with matching skills or in the same project
        query = db.query(User).filter(User.role == UserRole.VIEWER)
        
        if escalation.project_id:
            query = query.join(User.projects).filter(Project.id == escalation.project_id)
            
        # Fetch matching users
        potential_resolvers = query.all()
        
        if not potential_resolvers:
            return []
            
        # Format for AssignmentAgent
        resolvers_data = [
            {
                "id": str(u.id),
                "name": u.full_name,
                "expertise_tags": u.expertise_tags,
                "current_workload": u.current_escalation_count,
                "max_workload": u.max_concurrent_escalations
            }
            for u in potential_resolvers
        ]
        
        agent = AssignmentAgent()
        recommendation = agent.recommend_assignment(
            escalation_title=escalation.title,
            escalation_description=escalation.description,
            escalation_type=escalation.complaint_type or "other",
            escalation_priority=escalation.priority.value,
            available_resolvers=resolvers_data
        )
        
        if recommendation:
            # Store in ai_suggestions table
            from app.models.ai_suggestion import AISuggestion
            import json
            
            suggestion = AISuggestion(
                escalation_id=escalation.id,
                suggestion_type="assignment",
                content={
                    "recommended_user_id": recommendation.recommended_user_id,
                    "recommended_user_name": recommendation.recommended_user_name,
                    "reason": recommendation.reason,
                    "confidence": recommendation.confidence,
                    "alternative_user_id": recommendation.alternative_user_id,
                    "alternative_reason": recommendation.alternative_reason
                },
                confidence_score=recommendation.confidence
            )
            db.add(suggestion)
            
            # Also update escalation directly for compatibility
            # Convert string ID to UUID
            try:
                rec_id = UUID(recommendation.recommended_user_id)
                EscalationService.set_ai_recommendation(
                    db,
                    escalation.id,
                    rec_id,
                    recommendation.reason,
                    recommendation.confidence
                )
            except (ValueError, TypeError):
                pass
                
            db.commit()
            
        return resolvers_data

    @staticmethod
    def _map_type_to_project(db: Session, complaint_type: str) -> Optional[UUID]:
        """Map complaint type string to a project ID."""
        if not complaint_type:
            return None
            
        # Try to find a project with a similar name
        # Examples: "technical" -> "API Platform", "billing" -> "Billing Support"
        type_lower = complaint_type.lower()
        
        mapping = {
            "billing": "Billing Support",
            "technical": "API Platform",
            "product": "Feature Requests"
        }
        
        target_name = mapping.get(type_lower)
        if target_name:
            proj = db.query(Project).filter(Project.name == target_name).first()
            if proj:
                return proj.id
        
        # Fallback: keyword search in projects
        all_projects = db.query(Project).all()
        for p in all_projects:
            if type_lower in p.name.lower() or p.name.lower() in type_lower:
                return p.id
                
        return None

    @staticmethod
    def _add_timeline_event(
        db: Session,
        escalation_id: UUID,
        user_id: Optional[UUID],
        action_type: ActionType,
        description: str,
        metadata: dict = None
    ) -> TimelineEvent:
        """Add a timeline event (internal helper)."""
        event = TimelineEvent(
            escalation_id=escalation_id,
            user_id=user_id,
            action_type=action_type,
            description=description,
            event_metadata=metadata or {}
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
