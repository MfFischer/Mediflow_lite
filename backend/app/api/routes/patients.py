from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.patient import Patient
from app.models.audit_event import AuditEvent
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)

router = APIRouter()


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Log an audit event."""
    audit_event = AuditEvent(
        action=action,
        user_id=user_id,
        details=details
    )
    db.add(audit_event)
    db.commit()


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all patients with pagination and search.

    Accessible by all authenticated users.
    """
    query = db.query(Patient)

    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Patient.first_name.ilike(search_filter)) |
            (Patient.last_name.ilike(search_filter)) |
            (Patient.email.ilike(search_filter))
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    patients = query.offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "patients": patients
    }


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific patient by ID.

    Accessible by all authenticated users.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    return patient


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """
    Create a new patient.

    Accessible by admin, doctor, and receptionist roles.
    """
    # Check if email already exists
    existing_patient = db.query(Patient).filter(Patient.email == patient_data.email).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A patient with this email already exists"
        )

    # Create new patient
    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # Log audit event
    log_audit_event(
        db,
        "PATIENT_CREATED",
        current_user.id,
        f"User {current_user.username} created patient {new_patient.first_name} {new_patient.last_name}"
    )

    return new_patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """
    Update an existing patient.

    Accessible by admin, doctor, and receptionist roles.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Check if email is being changed and if it already exists
    if patient_data.email and patient_data.email != patient.email:
        existing_patient = db.query(Patient).filter(Patient.email == patient_data.email).first()
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A patient with this email already exists"
            )

    # Update patient fields
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    # Log audit event
    log_audit_event(
        db,
        "PATIENT_UPDATED",
        current_user.id,
        f"User {current_user.username} updated patient {patient.first_name} {patient.last_name}"
    )

    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Delete a patient.

    Only accessible by admin role.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

    # Log audit event before deletion
    log_audit_event(
        db,
        "PATIENT_DELETED",
        current_user.id,
        f"Admin {current_user.username} deleted patient {patient.first_name} {patient.last_name}"
    )

    db.delete(patient)
    db.commit()

    return None
