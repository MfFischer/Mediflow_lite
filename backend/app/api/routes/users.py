"""
User Management API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.audit_event import AuditEvent
from app.core.config import settings

router = APIRouter()


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Log an audit event."""
    if settings.enable_audit_log:
        audit_event = AuditEvent(
            action=action,
            user_id=user_id,
            details=details
        )
        db.add(audit_event)
        db.commit()


@router.get("/", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = Query(None, description="Filter by role (admin, doctor, receptionist)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users (admin only).
    Can filter by role to get doctors for appointments dropdown.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list users")
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view user details")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        prc_license=user_data.prc_license
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log audit event
    log_audit_event(
        db,
        "USER_CREATED",
        current_user.id,
        f"Admin {current_user.username} created user {new_user.username} with role {new_user.role}"
    )
    
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle password separately
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    elif "password" in update_data:
        update_data.pop("password")
    
    # Check username uniqueness if being updated
    if "username" in update_data and update_data["username"] != user.username:
        existing_user = db.query(User).filter(User.username == update_data["username"]).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check email uniqueness if being updated
    if "email" in update_data and update_data["email"] and update_data["email"] != user.email:
        existing_email = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log audit event
    log_audit_event(
        db,
        "USER_UPDATED",
        current_user.id,
        f"Admin {current_user.username} updated user {user.username}"
    )
    
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user (admin only).
    Cannot delete yourself.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    username = user.username
    
    db.delete(user)
    db.commit()
    
    # Log audit event
    log_audit_event(
        db,
        "USER_DELETED",
        current_user.id,
        f"Admin {current_user.username} deleted user {username}"
    )
    
    return {"message": f"User {username} deleted successfully"}

