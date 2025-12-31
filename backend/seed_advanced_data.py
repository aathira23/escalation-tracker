
import uuid
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.client import Client
from app.models.project import Project
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.tasks.email_ingestion import process_single_email

def seed_advanced_data():
    db = SessionLocal()
    try:
        print("Checking for Managers...")
        # Projects we want to target
        targets = {
            "Billing Support": {"manager_email": "manager.billing@support.com", "manager_name": "Bob Billing"},
            "Mobile App": {"manager_email": "manager.mobile@support.com", "manager_name": "Alice Apple"},
            "API Platform": {"manager_email": "john.doe@support.com", "manager_name": "John Doe"}
        }

        for p_name, info in targets.items():
            proj = db.query(Project).filter(Project.name == p_name).first()
            if not proj:
                print(f"Project {p_name} not found, skipping...")
                continue
            
            manager = db.query(User).filter(User.email == info["manager_email"]).first()
            if not manager:
                manager = AuthService.create_user(
                    db,
                    info["manager_email"],
                    "password123",
                    info["manager_name"],
                    UserRole.MANAGER
                )
                print(f"Created manager: {info['manager_name']}")
            
            if proj not in manager.projects:
                manager.projects.append(proj)
                print(f"Mapped {info['manager_name']} to {p_name}")

        db.commit()

        print("\nGenerating Mock Emails...")
        mock_emails = [
            {
                "email_id": f"seed-{uuid.uuid4()}",
                "sender_email": "billing@acmecorp.com",
                "sender_name": "Acme Billing Dept",
                "subject": "Critical: Overcharged on last 3 invoices",
                "body": "We have noticed a pattern of overcharging on our account. This is unacceptable. If not resolved, we will terminate our contract.",
                "received_at": datetime.utcnow()
            },
            {
                "email_id": f"seed-{uuid.uuid4()}",
                "sender_email": "dev-ops@techstart.io",
                "sender_name": "TechStart DevOps",
                "subject": "API Timeout issues on Production",
                "body": "Our production logs show constant timeouts when calling the /v1/auth endpoint. This is blocking our user logins.",
                "received_at": datetime.utcnow()
            },
            {
                "email_id": f"seed-{uuid.uuid4()}",
                "sender_email": "mobile@globalretail.com",
                "sender_name": "Global Retail Mobile Team",
                "subject": "App crashing on iOS 17",
                "body": "The latest SDK update is causing crashes on the new iOS version. We need a patch immediately.",
                "received_at": datetime.utcnow()
            }
        ]

        processed_count = 0
        
        print("\nSeeding additional team members for verification...")
        api_platform = db.query(Project).filter(Project.name == "API Platform").first()
        if api_platform:
            team_members = [
                {"email": "dev1.api@support.com", "name": "Dave API"},
                {"email": "dev2.api@support.com", "name": "Dan API"}
            ]
            for member_info in team_members:
                user = db.query(User).filter(User.email == member_info["email"]).first()
                if not user:
                    user = AuthService.create_user(db, member_info["email"], "password123", member_info["name"], UserRole.VIEWER)
                    print(f"Created viewer: {member_info['name']}")
                if api_platform not in user.projects:
                    user.projects.append(api_platform)
                    print(f"Mapped {member_info['name']} to API Platform")
        
        db.commit()

        for email in mock_emails:
            print(f"Processing: {email['subject']}")
            if process_single_email(db, email):
                processed_count += 1
            else:
                print(f"Failed to process {email['subject']}")

        print(f"\nSeeding complete! {processed_count} escalations created.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_advanced_data()
