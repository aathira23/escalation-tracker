
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.models.client import Client
from app.models.raw_complaint import RawComplaint

settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def check_state():
    print("\n--- Checking Clients ---")
    clients = db.query(Client).all()
    if not clients:
        print("WARNING: No clients found in database!")
    else:
        for c in clients:
            print(f"- {c.name} (Domain: {c.email_domain})")

    print("\n--- Checking Raw Complaints ---")
    complaints = db.query(RawComplaint).order_by(RawComplaint.received_at.desc()).limit(5).all()
    if not complaints:
        print("No complaints processed yet.")
    else:
        for rc in complaints:
            status = "Processed" if rc.processed else f"FAILED: {rc.processing_error}"
            print(f"- From: {rc.sender_email} | Subject: {rc.subject} | Status: {status}")

    print("\n-----------------------")

if __name__ == "__main__":
    check_state()
