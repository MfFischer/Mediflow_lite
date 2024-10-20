"""
E-Prescription API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import math
import random
import string

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.prescription import Prescription, Medication
from app.models.patient import Patient
from app.models.audit_event import AuditEvent
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
    PrescriptionWithDetails,
    PrescriptionListResponse
)


router = APIRouter()


def generate_prescription_number() -> str:
    """Generate a unique prescription number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"RX-{timestamp}-{random_suffix}"


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Helper to log audit events."""
    audit_event = AuditEvent(action=action, user_id=user_id, details=details)
    db.add(audit_event)
    db.commit()


@router.get("/", response_model=PrescriptionListResponse)
async def list_prescriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List prescriptions with pagination and filtering."""
    query = db.query(Prescription)
    
    # Apply filters
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Prescription.doctor_id == doctor_id)
    if is_active is not None:
        query = query.filter(Prescription.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    prescriptions = query.order_by(Prescription.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Build response with details
    items = []
    for rx in prescriptions:
        patient = db.query(Patient).filter(Patient.id == rx.patient_id).first()
        doctor = db.query(User).filter(User.id == rx.doctor_id).first()
        
        items.append(PrescriptionWithDetails(
            id=rx.id,
            prescription_number=rx.prescription_number,
            patient_id=rx.patient_id,
            doctor_id=rx.doctor_id,
            appointment_id=rx.appointment_id,
            diagnosis=rx.diagnosis,
            notes=rx.notes,
            is_active=rx.is_active,
            dispensed=rx.dispensed,
            dispensed_date=rx.dispensed_date,
            created_at=rx.created_at,
            updated_at=rx.updated_at,
            medications=[med for med in rx.medications],
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            patient_email=patient.email if patient else "",
            doctor_name=doctor.username if doctor else "Unknown"
        ))
    
    return PrescriptionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific prescription by ID."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found"
        )
    
    return prescription


@router.post("/", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """Create a new prescription (doctors only)."""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == prescription_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {prescription_data.patient_id} not found"
        )
    
    # Verify doctor exists
    doctor = db.query(User).filter(User.id == prescription_data.doctor_id).first()
    if not doctor or doctor.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {prescription_data.doctor_id} not found"
        )
    
    # Create prescription
    new_prescription = Prescription(
        prescription_number=generate_prescription_number(),
        patient_id=prescription_data.patient_id,
        doctor_id=prescription_data.doctor_id,
        appointment_id=prescription_data.appointment_id,
        diagnosis=prescription_data.diagnosis,
        notes=prescription_data.notes
    )
    
    db.add(new_prescription)
    db.flush()  # Get the prescription ID
    
    # Create medications
    for med_data in prescription_data.medications:
        medication = Medication(
            prescription_id=new_prescription.id,
            medication_name=med_data.medication_name,
            dosage=med_data.dosage,
            frequency=med_data.frequency,
            duration=med_data.duration,
            instructions=med_data.instructions
        )
        db.add(medication)
    
    db.commit()
    db.refresh(new_prescription)
    
    # Log audit event
    log_audit_event(
        db,
        "PRESCRIPTION_CREATED",
        current_user.id,
        f"Created prescription {new_prescription.prescription_number} for patient {patient.first_name} {patient.last_name}"
    )
    
    return new_prescription


@router.put("/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """Update an existing prescription."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found"
        )
    
    # Update fields
    update_data = prescription_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prescription, key, value)
    
    db.commit()
    db.refresh(prescription)
    
    # Log audit event
    log_audit_event(
        db,
        "PRESCRIPTION_UPDATED",
        current_user.id,
        f"Updated prescription {prescription.prescription_number}"
    )
    
    return prescription


@router.post("/{prescription_id}/dispense", response_model=PrescriptionResponse)
async def dispense_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "receptionist"]))
):
    """Mark a prescription as dispensed."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prescription {prescription_id} not found"
        )
    
    if prescription.dispensed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescription already dispensed"
        )
    
    prescription.dispensed = True
    prescription.dispensed_date = datetime.utcnow()
    
    db.commit()
    db.refresh(prescription)
    
    # Log audit event
    log_audit_event(
        db,
        "PRESCRIPTION_DISPENSED",
        current_user.id,
        f"Dispensed prescription {prescription.prescription_number}"
    )
    
    return prescription

