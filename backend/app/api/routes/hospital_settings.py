"""
Hospital Settings API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.hospital_settings import HospitalSettings
from app.schemas.hospital_settings import HospitalSettingsCreate, HospitalSettingsUpdate, HospitalSettingsResponse
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=HospitalSettingsResponse)
def get_hospital_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get hospital settings (returns first record or creates default)."""
    settings = db.query(HospitalSettings).first()
    
    if not settings:
        # Create default settings if none exist
        settings = HospitalSettings(
            hospital_name="Medical Center",
            invoice_prefix="INV"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/{settings_id}", response_model=HospitalSettingsResponse)
def update_hospital_settings(
    settings_id: int,
    settings_update: HospitalSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update hospital settings (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update hospital settings")
    
    settings = db.query(HospitalSettings).filter(HospitalSettings.id == settings_id).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Hospital settings not found")
    
    # Update fields
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings


@router.post("/", response_model=HospitalSettingsResponse)
def create_hospital_settings(
    settings_create: HospitalSettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create hospital settings (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create hospital settings")
    
    # Check if settings already exist
    existing = db.query(HospitalSettings).first()
    if existing:
        raise HTTPException(status_code=400, detail="Hospital settings already exist. Use PUT to update.")
    
    settings = HospitalSettings(**settings_create.dict())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    return settings

