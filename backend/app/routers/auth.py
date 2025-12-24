"""
Authentication Router
Handles login, registration, and current user info.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse, Token
from app.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return Token(accessToken=access_token, tokenType="bearer")


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Register a new user (admin only).
    """
    # Check if email already exists
    existing = AuthService.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = AuthService.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=UserRole(user_data.role.value),
        expertise_tags=user_data.expertise_tags,
        max_concurrent_escalations=user_data.max_concurrent_escalations
    )
    
    return UserResponse.from_orm_model(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return UserResponse.from_orm_model(current_user)


@router.post("/setup-admin", response_model=UserResponse)
async def setup_initial_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create initial admin user (only works if no users exist).
    This endpoint is for initial setup only.
    """
    # Check if any users exist
    existing_users = db.query(User).first()
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin setup already completed. Use /register with admin credentials."
        )
    
    user = AuthService.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=UserRole.ADMIN,  # Force admin role for first user
        expertise_tags=user_data.expertise_tags,
        max_concurrent_escalations=user_data.max_concurrent_escalations
    )
    
    return UserResponse.from_orm_model(user)
