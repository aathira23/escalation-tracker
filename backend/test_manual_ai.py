
from app.database import SessionLocal
from app.models.escalation import Escalation, EscalationStatus
from app.models.client import Client
from app.models.user import User, UserRole
from app.models.ai_suggestion import AISuggestion
from app.services.escalation_service import EscalationService
import uuid

def test_manual_ai_trigger():
    db = SessionLocal()
    try:
        # Get a client and an admin
        client = db.query(Client).first()
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not client or not admin:
            print("Missing seed data (client/admin)")
            return

        print(f"Creating manual escalation for client: {client.name}")
        
        # Create manual escalation directly via service (simulating router)
        escalation = EscalationService.create_escalation(
            db,
            title="Manual Test: Billing Overcharge Found",
            description="We manually found an overcharge of $500 on the last invoice.",
            client_id=client.id,
            created_by=admin.id
        )
        
        print(f"Created Escalation: {escalation.id}")
        
        # Check suggestions BEFORE AI processing (should be 0)
        s_before = db.query(AISuggestion).filter(AISuggestion.escalation_id == escalation.id).count()
        print(f"Suggestions before AI: {s_before}")
        
        # Trigger Unified AI Processing
        print("Triggering AI Intelligence...")
        EscalationService.process_ai_intelligence(db, escalation.id)
        
        # Check suggestions AFTER AI processing
        suggestions = db.query(AISuggestion).filter(AISuggestion.escalation_id == escalation.id).all()
        print(f"Suggestions after AI: {len(suggestions)}")
        for s in suggestions:
            print(f"  - Type: {s.suggestion_type}, Priority: {escalation.priority.value}")
            if s.suggestion_type == 'resolution':
                print(f"    Content: {s.content.get('steps')}")

        if len(suggestions) > 0:
            print("\nSUCCESS: Manual escalation triggered AI processing!")
        else:
            print("\nFAILED: No suggestions generated for manual escalation.")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_manual_ai_trigger()
