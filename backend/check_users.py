
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_users():
    try:
        users = db.query(User).all()
        if users:
            print("Existing users:")
            for user in users:
                print(f"Email: {user.email}, Role: {user.role.value}")
        else:
            print("No users found. Creating default admin...")
            try:
                AuthService.create_user(
                    db=db,
                    email="admin@example.com",
                    password="adminpassword",
                    full_name="System Admin",
                    role=UserRole.ADMIN
                )
                print("Created default admin:")
                print("Email: admin@example.com")
                print("Password: adminpassword")
            except Exception as e:
                print(f"Failed to create admin: {e}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
