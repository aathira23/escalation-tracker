"""
Authentication Service
Handles user authentication, password hashing, and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User, UserRole

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.VIEWER,
        expertise_tags: Optional[List[str]] = None,
        max_concurrent_escalations: int = 5,
        department_id: Optional[UUID] = None
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=AuthService.get_password_hash(password),
            full_name=full_name,
            role=role,
            expertise_tags=expertise_tags or [],
            max_concurrent_escalations=max_concurrent_escalations,
            department_id=department_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get a user by their ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by their email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_all_users(db: Session, include_inactive: bool = False) -> List[User]:
        """Get all users."""
        query = db.query(User)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.all()
    
    @staticmethod
    def get_users_by_role(db: Session, role: UserRole) -> List[User]:
        """Get all active users with a specific role."""
        return db.query(User).filter(
            User.role == role,
            User.is_active == True
        ).all()
