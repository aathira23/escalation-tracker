
import asyncio
from app.database import SessionLocal
from app.models.escalation import Escalation
from app.services.escalation_service import EscalationService
from app.models.ai_suggestion import AISuggestion

async def verify_ai():
    db = SessionLocal()
    try:
        # Find an escalation to re-process
        escalation = db.query(Escalation).first()
        if not escalation:
            print("No escalations found to test.")
            return
            
        print(f"Re-processing Escalation: {escalation.title}")
        print(f"Original Priority: {escalation.priority}")
        
        # Clear old suggestions to be sure
        db.query(AISuggestion).filter(AISuggestion.escalation_id == escalation.id).delete()
        db.commit()
        
        # Trigger AI intelligence
        EscalationService.process_ai_intelligence(db, escalation.id)
        
        # Refresh and check
        db.refresh(escalation)
        print(f"New Priority: {escalation.priority}")
        print(f"Executive Summary: {escalation.executive_summary}")
        
        suggestions = db.query(AISuggestion).filter(AISuggestion.escalation_id == escalation.id).all()
        for s in suggestions:
            print(f"\nSuggestion Type: {s.suggestion_type}")
            print(f"Content: {s.content}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_ai())
