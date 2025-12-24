"""
SLA Monitor Task
Checks for escalations approaching or past their SLA deadline.
"""
from datetime import datetime, timedelta

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.escalation import Escalation, EscalationStatus
from app.models.timeline import TimelineEvent, ActionType
from sqlalchemy import and_


@celery_app.task(name="app.tasks.sla_monitor.check_sla_deadlines")
def check_sla_deadlines() -> dict:
    """
    Daily task to check SLA deadlines and create warnings/alerts.
    
    Triggers:
    - SLA warning: < 7 days remaining
    - SLA breach: past due date
    """
    db = SessionLocal()
    now = datetime.utcnow()
    warning_threshold = now + timedelta(days=7)
    
    warnings_created = 0
    breaches_created = 0
    
    try:
        # Find open/in-progress escalations
        active_escalations = db.query(Escalation).filter(
            Escalation.status.in_([EscalationStatus.OPEN, EscalationStatus.IN_PROGRESS])
        ).all()
        
        for escalation in active_escalations:
            # Check for breach (overdue)
            if escalation.due_date < now:
                # Check if breach was already recorded today
                existing_breach = db.query(TimelineEvent).filter(
                    and_(
                        TimelineEvent.escalation_id == escalation.id,
                        TimelineEvent.action_type == ActionType.SLA_BREACH,
                        TimelineEvent.created_at >= now.replace(hour=0, minute=0, second=0)
                    )
                ).first()
                
                if not existing_breach:
                    days_overdue = (now - escalation.due_date).days
                    event = TimelineEvent(
                        escalation_id=escalation.id,
                        user_id=None,  # System event
                        action_type=ActionType.SLA_BREACH,
                        description=f"SLA BREACH: Escalation is {days_overdue} days overdue",
                        metadata={"days_overdue": days_overdue, "due_date": escalation.due_date.isoformat()}
                    )
                    db.add(event)
                    breaches_created += 1
                    
            # Check for warning (approaching deadline)
            elif escalation.due_date <= warning_threshold:
                # Check if warning was already recorded today
                existing_warning = db.query(TimelineEvent).filter(
                    and_(
                        TimelineEvent.escalation_id == escalation.id,
                        TimelineEvent.action_type == ActionType.SLA_WARNING,
                        TimelineEvent.created_at >= now.replace(hour=0, minute=0, second=0)
                    )
                ).first()
                
                if not existing_warning:
                    days_remaining = (escalation.due_date - now).days
                    event = TimelineEvent(
                        escalation_id=escalation.id,
                        user_id=None,  # System event
                        action_type=ActionType.SLA_WARNING,
                        description=f"SLA Warning: Only {days_remaining} days remaining until deadline",
                        metadata={"days_remaining": days_remaining, "due_date": escalation.due_date.isoformat()}
                    )
                    db.add(event)
                    warnings_created += 1
        
        db.commit()
        
        return {
            "checked": len(active_escalations),
            "warnings_created": warnings_created,
            "breaches_created": breaches_created
        }
        
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.sla_monitor.send_notifications")
def send_notifications() -> dict:
    """
    Send notifications to resolvers and managers for SLA warnings/breaches.
    
    TODO: Implement actual notification sending (email, Slack, etc.)
    For now, this just logs the notifications that would be sent.
    """
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        # Get today's warnings and breaches
        events = db.query(TimelineEvent).filter(
            and_(
                TimelineEvent.action_type.in_([ActionType.SLA_WARNING, ActionType.SLA_BREACH]),
                TimelineEvent.created_at >= now.replace(hour=0, minute=0, second=0)
            )
        ).all()
        
        notifications = []
        for event in events:
            escalation = event.escalation
            notification = {
                "type": event.action_type.value,
                "escalation_id": str(escalation.id),
                "escalation_title": escalation.title,
                "assignee_id": str(escalation.assigned_to) if escalation.assigned_to else None,
                "message": event.description
            }
            notifications.append(notification)
            # TODO: Actually send notification (email, Slack, etc.)
        
        return {
            "notifications_queued": len(notifications),
            "details": notifications
        }
        
    finally:
        db.close()
