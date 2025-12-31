
from app.database import SessionLocal
from app.models.escalation import Escalation
from app.models.ai_suggestion import AISuggestion
from app.models.raw_complaint import RawComplaint
import json

def check_ai_suggestions():
    db = SessionLocal()
    try:
        # Check raw complaints too
        raws = db.query(RawComplaint).all()
        print(f"Total Raw Complaints: {len(raws)}")
        for r in raws:
            if r.processing_error:
                print(f"  Raw ID {r.id}: ERROR: {r.processing_error}")
        
        print("\n" + "="*50)
        escalations = db.query(Escalation).order_by(Escalation.created_at.asc()).all()
        print(f"Total Escalations: {len(escalations)}")
        print("-" * 50)
        
        for e in escalations:
            suggestions = db.query(AISuggestion).filter(AISuggestion.escalation_id == e.id).all()
            types = [s.suggestion_type for s in suggestions]
            print(f"[{e.created_at}] Escalation: {e.title}")
            print(f"  ID: {e.id}")
            print(f"  Suggestions found: {len(suggestions)} ({', '.join(types)})")
            
            # Check if there's a corresponding RawComplaint
            raw = db.query(RawComplaint).filter(RawComplaint.escalation_id == e.id).first()
            if not raw:
                print("  (Legacy/Manual - No RawComplaint found)")
            
            print("-" * 30)
            
    finally:
        db.close()

if __name__ == "__main__":
    check_ai_suggestions()
