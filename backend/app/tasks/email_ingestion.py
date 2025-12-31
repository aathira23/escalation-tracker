"""
Email Ingestion Task
Fetches complaints from email (IMAP) or mock data for development.
"""
import uuid
from datetime import datetime
from typing import Optional

from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.database import SessionLocal
from app.models.raw_complaint import RawComplaint
from app.models.client import Client
from app.models.user import User, UserRole
from app.agents.complaint_agent import ComplaintIntelligenceAgent
from app.services.escalation_service import EscalationService

settings = get_settings()


# Mock email data for development
MOCK_EMAILS = [
    {
        "email_id": f"mock-{uuid.uuid4()}",
        "sender_email": "john.smith@acmecorp.com",
        "sender_name": "John Smith",
        "subject": "Billing Issue - Invoice #12345",
        "body": """Hello,

I'm extremely frustrated with the billing situation. We were charged twice for the same service in November, and despite multiple support tickets, this hasn't been resolved.

Our finance team has been waiting for over 3 weeks for a refund. This is unacceptable and is causing serious issues with our monthly reconciliation.

Please escalate this immediately.

Regards,
John Smith
Finance Director, ACME Corp""",
        "received_at": datetime.utcnow()
    },
    {
        "email_id": f"mock-{uuid.uuid4()}",
        "sender_email": "sarah.jones@techstart.io",
        "sender_name": "Sarah Jones",
        "subject": "API Performance Issues - Urgent",
        "body": """Hi,

We've been experiencing significant latency issues with your API since last Thursday. Our application response times have degraded by 300% and our users are complaining.

This is a critical issue for us as it's affecting our production environment.

Can someone please look into this urgently?

Thanks,
Sarah Jones
CTO, TechStart""",
        "received_at": datetime.utcnow()
    },
    {
        "email_id": f"mock-{uuid.uuid4()}",
        "sender_email": "mike.chen@globalretail.com",
        "sender_name": "Mike Chen",
        "subject": "Missing Features in Latest Update",
        "body": """Hello Support,

The latest product update removed several features that we rely on daily. Specifically:
- The advanced search functionality
- Custom report templates
- Bulk export option

Was this intentional? We weren't notified about any deprecation. This is quite disruptive to our workflow.

Please advise.

Best,
Mike Chen
Operations Manager""",
        "received_at": datetime.utcnow()
    },

    {
        "email_id": f"mock-{uuid.uuid4()}",
        "sender_email": "alice@example.com",
        "sender_name": "Alice Bob",
        "subject": "testing the workflow, confused if it will work",
        "body": """Hello Team,

This is extremely frustrating. We have been charged twice for the same service
in our latest invoice, and despite multiple follow-ups, no one has responded.

This is unacceptable for a paying customer. If this is not resolved immediately,
we will have to reconsider continuing with your services.

Please treat this as urgent.

Regards""",
        "received_at": datetime.utcnow()
    },
]


@celery_app.task(name="app.tasks.email_ingestion.process_incoming_emails")
def process_incoming_emails(manual_trigger_email_id: Optional[str] = None):
    """
    Periodic task to fetch and process incoming complaint emails.
    Uses mock data if MOCK_EMAIL_INGESTION is enabled.
    """
    if settings.mock_email_ingestion:
        return process_mock_emails(manual_trigger_email_id)
    else:
        return process_imap_emails()


def process_mock_emails(manual_trigger_email_id: Optional[str] = None) -> dict:
    """
    Process mock emails for development/testing.
    Creates one random mock email per invocation OR a specific one if triggered.
    """
    import random
    
    db = SessionLocal()
    try:
        if manual_trigger_email_id:
            # excessive logic to find the specific email
            # We need to find the dict in MOCK_EMAILS where email_id matches?
            # Wait, MOCK_EMAILS generates UUIDs dynamically in the list definition!
            # The list defined at the top of the file has f"mock-{uuid.uuid4()}" executed AT IMPORT TIME.
            # So the IDs are stable after import.
            
            # Find the mock email with matching ID
            mock = next((m for m in MOCK_EMAILS if m["email_id"] == manual_trigger_email_id), None)
            if not mock:
                return {"processed": 0, "error": f"Mock email with ID {manual_trigger_email_id} not found"}
        else:
            # Default behavior: Randomly pick one
            mock = random.choice(MOCK_EMAILS)
            
        mock_copy = mock.copy()
        
        # If it's a manual trigger, we use the existing ID.
        # If it's random auto-gen, we USUALLY want a new ID to simulate fresh email?
        # But if we want to "send" the SPECIFIC mock email defined in the file, we should probably keep its ID?
        # The original code generated a NEW ID every time: mock["email_id"] = f"mock-{uuid.uuid4()}"
        
        if not manual_trigger_email_id:
             mock_copy["email_id"] = f"mock-{uuid.uuid4()}"
        
        result = process_single_email(db, mock_copy)
        return {
            "processed": 1 if result else 0,
            "mode": "mock",
            "email_id": mock_copy["email_id"]
        }
    finally:
        db.close()


def process_imap_emails() -> dict:
    """
    Fetch emails from IMAP server (production mode).
    Uses EmailService for connection and parsing.
    """
    try:
        from app.services.email_service import EmailService
    except ImportError:
        return {"error": "EmailService dependencies missing", "processed": 0}
    
    db = SessionLocal()
    processed = 0
    errors = 0
    
    try:
        # Fetch unread emails using the service
        # It handles connection, folder selection, and parsing
        emails = EmailService.fetch_unread_emails(limit=20)
        
        if not emails:
            return {"processed": 0, "mode": "imap", "status": "no_emails"}
            
        for email_data in emails:
            uid = email_data.pop("uid") # Remove IMAP UID from data passed to processor
            
            try:
                success = process_single_email(db, email_data)
                
                # Mark as processed (move folder or flag)
                EmailService.mark_as_processed(uid, success)
                
                if success:
                    processed += 1
                else:
                    errors += 1
                    
            except Exception as e:
                print(f"Error processing email {email_data.get('email_id')}: {e}")
                errors += 1
                # Still try to mark as processed/flagged so we don't loop forever?
                # For now, maybe just leave it as unseen if it crashed hard?
                # Or better, mark as Seen so valid ones aren't blocked?
                # Let's rely on mark_as_processed default behavior (flagging)
                try:
                    EmailService.mark_as_processed(uid, False)
                except:
                    pass
        
        return {"processed": processed, "errors": errors, "mode": "imap"}
        
    except Exception as e:
        return {"error": str(e), "processed": processed}
    finally:
        db.close()


def process_single_email(db, email_data: dict) -> bool:
    """
    Process a single email: store, analyze with AI, and create escalation.
    
    Returns True if successfully processed, False otherwise.
    """
    try:
        # Check if already processed
        existing = db.query(RawComplaint).filter(
            RawComplaint.email_id == email_data["email_id"]
        ).first()
        
        if existing:
            return False
        
        # Store raw complaint
        raw_complaint = RawComplaint(
            email_id=email_data["email_id"],
            sender_email=email_data["sender_email"],
            sender_name=email_data.get("sender_name"),
            subject=email_data["subject"],
            body=email_data["body"],
            received_at=email_data["received_at"]
        )
        db.add(raw_complaint)
        db.commit()
        
        # Find matching client by email domain
        email_domain = email_data["sender_email"].split("@")[-1] if "@" in email_data["sender_email"] else None
        client = None
        
        if email_domain:
            client = db.query(Client).filter(Client.email_domain == email_domain).first()
        
        if not client:
            # Check specific contact emails
            client = db.query(Client).filter(
                Client.contact_emails.contains([email_data["sender_email"]])
            ).first()
        
        if not client:
            # No matching client - mark as unprocessable
            raw_complaint.processing_error = "No matching client found"
            db.commit()
            return False
        
        # Get system user for creation (or first admin)
        system_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not system_user:
            raw_complaint.processing_error = "No admin user available to create escalation"
            db.commit()
            return False
            
        # Create escalation
        escalation = EscalationService.create_escalation(
            db,
            title=email_data["subject"][:500], # Initial title
            description=email_data["body"],
            client_id=client.id,
            project_id=None, # Will be mapped by AI
            created_by=system_user.id
        )
        
        # Trigger Unified AI Processing
        EscalationService.process_ai_intelligence(db, escalation.id)
        
        # Link raw complaint to escalation
        raw_complaint.processed = True
        raw_complaint.escalation_id = escalation.id
        db.commit()
        
        return True
        
    except Exception as e:
        db.rollback()
        if 'raw_complaint' in locals():
            raw_complaint.processing_error = str(e)
            db.commit()
        return False