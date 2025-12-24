"""
Users Router
Handles user management endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.auth_service import AuthService
from app.dependencies import get_current_user, require_manager_or_admin, require_admin
from app.models.user import User, UserRole
from app.models.project import Project
from app.schemas.user import UserResponse, UserUpdate, UserCreate

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    role: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    List users.
    Admins see everyone.
    Managers see users in their projects.
    """
    query = db.query(User)
    
    if not include_inactive:
        query = query.filter(User.is_active == True)
        
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

    # Manager filtering: only see users in shared projects
    if current_user.role == UserRole.MANAGER:
        project_ids = [p.id for p in current_user.projects]
        query = query.join(User.projects).filter(Project.id.in_(project_ids))
    
    users = query.all()
    return [UserResponse.from_orm_model(u) for u in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user (admin only).
    """
    # Check if user already exists
    existing = AuthService.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = AuthService.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=UserRole(user_data.role.value),
        expertise_tags=user_data.expertise_tags,
        max_concurrent_escalations=user_data.max_concurrent_escalations
    )
    
    return UserResponse.from_orm_model(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID.
    Users can view their own profile; managers/admins can view anyone.
    """
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm_model(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user details.
    Users can update their own name; admins can update roles and other fields.
    """
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Permission check
    is_self = current_user.id == user_id
    is_admin = current_user.role == UserRole.ADMIN
    
    if not is_self and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Self can only update name; admin can update everything
    if is_self and not is_admin:
        if any([user_data.role, user_data.is_active is not None, user_data.expertise_tags, user_data.max_concurrent_escalations]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update role, status, and expertise settings"
            )
    
    # Apply updates
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.role and is_admin:
        user.role = UserRole(user_data.role.value)
    if user_data.expertise_tags is not None and is_admin:
        user.expertise_tags = user_data.expertise_tags
    if user_data.max_concurrent_escalations and is_admin:
        user.max_concurrent_escalations = user_data.max_concurrent_escalations
    if user_data.is_active is not None and is_admin:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm_model(user)


@router.get("/resolvers/available", response_model=list[UserResponse])
async def get_available_resolvers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Get viewers who can be assigned as resolvers.
    Filters out users at max capacity.
    """
    viewers = AuthService.get_users_by_role(db, UserRole.VIEWER)
    
    # Filter users who have capacity
    available = [
        u for u in viewers 
        if u.current_escalation_count < u.max_concurrent_escalations
    ]
    
    return [UserResponse.from_orm_model(u) for u in available]
