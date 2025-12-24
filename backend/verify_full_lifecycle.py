import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from app.database import SessionLocal
from app.tasks.email_ingestion import process_single_email
from app.models.escalation import Escalation
from app.models.ai_suggestion import AISuggestion
from app.models.user import User, UserRole
from app.models.project import Project
from datetime import datetime
import uuid

def verify_lifecycle():
    print("--- Verifying Full Escalation Lifecycle ---")
    db = SessionLocal()
    try:
        # Mock email data
        email_data = {
            "email_id": f"test-{uuid.uuid4()}",
            "sender_email": "john.smith@acmecorp.com",
            "sender_name": "John Smith",
            "subject": "Urgent Billing Issue: Double Charge",
            "body": "I've been charged twice for my subscription this month. Please refund the $99.99 immediately.",
            "received_at": datetime.utcnow()
        }
        
        print(f"1. Processing mock email: {email_data['subject']}")
        result = process_single_email(db, email_data)
        
        if not result:
            print("FAILED: process_single_email returned False. Check if client 'ACME Corp' exists.")
            return

        # Fetch the created escalation
        escalation = db.query(Escalation).filter(Escalation.title.contains("Billing Issue")).order_by(Escalation.created_at.desc()).first()
        
        if not escalation:
            print("FAILED: Escalation not found in database.")
            return
            
        print(f"SUCCESS: Escalation created: {escalation.id}")
        print(f"Title: {escalation.title}")
        print(f"Project ID: {escalation.project_id}")
        
        # Check project mapping
        if escalation.project_id:
            project = db.query(Project).filter(Project.id == escalation.project_id).first()
            print(f"Mapped to Project: {project.name if project else 'Unknown'}")
        else:
            print("WARNING: Escalation not mapped to any project.")

        # Check AI Suggestions
        suggestions = db.query(AISuggestion).filter(AISuggestion.escalation_id == escalation.id).all()
        print(f"Number of AI Suggestions found: {len(suggestions)}")
        for s in suggestions:
            print(f"- Suggestion Type: {s.suggestion_type}")
            print(f"  Content: {s.content}")

        # Verify Assignment Recommendation in Escalation
        if escalation.ai_recommended_assignee_id:
            assignee = db.query(User).filter(User.id == escalation.ai_recommended_assignee_id).first()
            print(f"AI Recommended Assignee: {assignee.full_name if assignee else 'Unknown'}")
            print(f"AI Reason: {escalation.ai_assignment_reason}")
        else:
            print("WARNING: No AI recommendation stored in escalation.")

        print("\n--- Lifecycle Verification Complete ---")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_lifecycle()
