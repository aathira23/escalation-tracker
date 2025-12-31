
import asyncio
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate
from fastapi import HTTPException
from app.routers.users import update_user

async def test_manager_update_permission():
    db = SessionLocal()
    try:
        # Find Manager John Doe (API Platform)
        john = db.query(User).filter(User.email == "john.doe@support.com").first()
        # Find Teammate Dave API (API Platform)
        dave = db.query(User).filter(User.email == "dev1.api@support.com").first()
        
        print(f"Manager: {john.full_name}")
        print(f"Teammate: {dave.full_name}")
        
        # Mock current_user as John
        current_user = john
        
        # Attempt to update Dave's name
        update_data = UserUpdate(full_name="Dave API Updated")
        try:
            await update_user(dave.id, update_data, db, current_user)
            print(f"SUCCESS: Manager {john.full_name} updated teammate {dave.full_name}")
        except HTTPException as e:
            print(f"FAILED: {e.detail}")

        # Attempt to update Dave's role (should fail)
        update_data_role = UserUpdate(role=UserRole.ADMIN)
        try:
            await update_user(dave.id, update_data_role, db, current_user)
            print("FAILED: Manager was able to upgrade role (Expected Failure)")
        except HTTPException as e:
            print(f"SUCCESS: Role update blocked as expected: {e.detail}")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_manager_update_permission())
