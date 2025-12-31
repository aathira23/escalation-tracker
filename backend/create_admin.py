from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

def create_admin():
    db = SessionLocal()
    try:
        email = "admin@example.com"
        print(f"Checking for admin user: {email}")
        user = AuthService.get_user_by_email(db, email)
        if not user:
            print("Creating Admin User...")
            user = AuthService.create_user(
                db, 
                email, 
                "adminpassword", 
                "System Admin", 
                UserRole.ADMIN,
                expertise_tags=["admin"]
            )
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
            if user.role != UserRole.ADMIN:
                print(f"Updating role for {email} to ADMIN")
                user.role = UserRole.ADMIN
                db.commit()
                
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
