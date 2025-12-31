
import asyncio
from uuid import UUID
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.escalation import Escalation, EscalationStatus
from app.models.project import Project
from app.routers.escalations import update_escalation_status, assign_escalation
from app.schemas.escalation import EscalationStatusUpdate, EscalationAssign
from fastapi import HTTPException

async def test_permissions():
    db = SessionLocal()
    try:
        # 1. Setup participants
        # John Doe is manager of API Platform (Engineering/Technical department probably)
        john = db.query(User).filter(User.email == "john.doe@support.com").first()
        # Bob Billing is manager of Billing Support
        bob = db.query(User).filter(User.email == "manager.billing@support.com").first()
        # Dave is in API Platform
        dave = db.query(User).filter(User.email == "dev1.api@support.com").first()
        
        # 2. Find an escalation in John's project (API Platform)
        api_project = db.query(Project).filter(Project.name == "API Platform").first()
        billing_project = db.query(Project).filter(Project.name == "Billing Support").first()
        
        api_escalation = db.query(Escalation).filter(Escalation.project_id == api_project.id).first()
        if not api_escalation:
            print("Creating mock API escalation...")
            api_escalation = Escalation(
                title="API Timeout Issue",
                description="The API is timing out for several clients.",
                client_id=db.query(User).filter(User.role == UserRole.VIEWER).first().managed_clients[0].id,
                project_id=api_project.id,
                created_by=john.id,
                status=EscalationStatus.OPEN
            )
            db.add(api_escalation)
            db.commit()
            db.refresh(api_escalation)

        billing_escalation = db.query(Escalation).filter(Escalation.project_id == billing_project.id).first()
        if not billing_escalation:
             print("Creating mock Billing escalation...")
             billing_escalation = Escalation(
                title="Invoice Error",
                description="Client was double charged.",
                client_id=db.query(User).filter(User.role == UserRole.VIEWER).first().managed_clients[0].id,
                project_id=billing_project.id,
                created_by=bob.id,
                status=EscalationStatus.OPEN
            )
             db.add(billing_escalation)
             db.commit()
             db.refresh(billing_escalation)

        print(f"\nTesting with Manager: {john.full_name} (Dept: {john.department.name if john.department else 'N/A'})")
        
        # TEST 1: Manager John should be able to update API escalation
        print(f"--- Test 1: Manager updates own department escalation ---")
        status_update = EscalationStatusUpdate(status=EscalationStatus.IN_PROGRESS, note="Starting work")
        try:
            await update_escalation_status(api_escalation.id, status_update, db, john)
            print("SUCCESS: John updated API escalation status.")
        except HTTPException as e:
            print(f"FAILED: John could not update API escalation: {e.detail}")

        # TEST 2: Manager John should NOT be able to update Billing escalation
        print(f"\n--- Test 2: Manager updates other department escalation (Should fail) ---")
        try:
            await update_escalation_status(billing_escalation.id, status_update, db, john)
            print("FAILED: John was able to update Billing escalation (Unexpected)")
        except HTTPException as e:
            print(f"SUCCESS: John blocked from updating Billing escalation: {e.detail}")

        # TEST 3: Manager John assigns team member in own department
        print(f"\n--- Test 3: Manager assigns team member in own department ---")
        assignment = EscalationAssign(assignee_id=dave.id, reason="Dave is the expert here")
        try:
            await assign_escalation(api_escalation.id, assignment, db, john)
            print(f"SUCCESS: John assigned {dave.full_name} to API escalation.")
        except HTTPException as e:
            print(f"FAILED: John could not assign Dave: {e.detail}")

        # TEST 4: Manager John assigns team member to Billing escalation (Should fail)
        print(f"\n--- Test 4: Manager assigns to other department escalation (Should fail) ---")
        try:
             await assign_escalation(billing_escalation.id, assignment, db, john)
             print("FAILED: John was able to assign to Billing escalation (Unexpected)")
        except HTTPException as e:
             print(f"SUCCESS: John blocked from assigning to Billing escalation: {e.detail}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_permissions())
