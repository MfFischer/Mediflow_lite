"""
Lab Results API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import math
import random
import string

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.lab_result import LabResult, LabTestValue, LabResultStatus
from app.models.patient import Patient
from app.models.audit_event import AuditEvent
from app.schemas.lab_result import (
    LabResultCreate,
    LabResultUpdate,
    LabResultResponse,
    LabResultWithDetails,
    LabResultListResponse
)


router = APIRouter()


def generate_result_number() -> str:
    """Generate a unique lab result number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"LAB-{timestamp}-{random_suffix}"


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Helper to log audit events."""
    audit_event = AuditEvent(action=action, user_id=user_id, details=details)
    db.add(audit_event)
    db.commit()


@router.get("/", response_model=LabResultListResponse)
async def list_lab_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[LabResultStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List lab results with pagination and filtering."""
    query = db.query(LabResult)
    
    # Apply filters
    if patient_id:
        query = query.filter(LabResult.patient_id == patient_id)
    if doctor_id:
        query = query.filter(LabResult.doctor_id == doctor_id)
    if status:
        query = query.filter(LabResult.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    lab_results = query.order_by(LabResult.test_date.desc()).offset(offset).limit(page_size).all()
    
    # Build response with details
    items = []
    for result in lab_results:
        patient = db.query(Patient).filter(Patient.id == result.patient_id).first()
        doctor = db.query(User).filter(User.id == result.doctor_id).first()
        
        items.append(LabResultWithDetails(
            id=result.id,
            result_number=result.result_number,
            patient_id=result.patient_id,
            doctor_id=result.doctor_id,
            appointment_id=result.appointment_id,
            test_name=result.test_name,
            test_category=result.test_category,
            status=result.status,
            test_date=result.test_date,
            result_date=result.result_date,
            reviewed_date=result.reviewed_date,
            notes=result.notes,
            doctor_comments=result.doctor_comments,
            created_at=result.created_at,
            updated_at=result.updated_at,
            test_values=[val for val in result.test_values],
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            patient_email=patient.email if patient else "",
            doctor_name=doctor.username if doctor else "Unknown"
        ))
    
    return LabResultListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )


@router.get("/{result_id}", response_model=LabResultResponse)
async def get_lab_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific lab result by ID."""
    lab_result = db.query(LabResult).filter(LabResult.id == result_id).first()
    
    if not lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab result {result_id} not found"
        )
    
    return lab_result


@router.post("/", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_result(
    result_data: LabResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """Create a new lab result."""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == result_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {result_data.patient_id} not found"
        )
    
    # Verify doctor exists
    doctor = db.query(User).filter(User.id == result_data.doctor_id).first()
    if not doctor or doctor.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {result_data.doctor_id} not found"
        )
    
    # Create lab result
    new_result = LabResult(
        result_number=generate_result_number(),
        patient_id=result_data.patient_id,
        doctor_id=result_data.doctor_id,
        appointment_id=result_data.appointment_id,
        test_name=result_data.test_name,
        test_category=result_data.test_category,
        test_date=result_data.test_date,
        notes=result_data.notes
    )
    
    db.add(new_result)
    db.flush()  # Get the result ID
    
    # Create test values
    for value_data in result_data.test_values:
        test_value = LabTestValue(
            lab_result_id=new_result.id,
            parameter_name=value_data.parameter_name,
            value=value_data.value,
            unit=value_data.unit,
            reference_range=value_data.reference_range,
            is_abnormal=value_data.is_abnormal
        )
        db.add(test_value)
    
    db.commit()
    db.refresh(new_result)
    
    # Log audit event
    log_audit_event(
        db,
        "LAB_RESULT_CREATED",
        current_user.id,
        f"Created lab result {new_result.result_number} for patient {patient.first_name} {patient.last_name}"
    )
    
    return new_result


@router.put("/{result_id}", response_model=LabResultResponse)
async def update_lab_result(
    result_id: int,
    result_data: LabResultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """Update an existing lab result."""
    lab_result = db.query(LabResult).filter(LabResult.id == result_id).first()
    
    if not lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab result {result_id} not found"
        )
    
    # Update fields
    update_data = result_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lab_result, key, value)
    
    db.commit()
    db.refresh(lab_result)
    
    # Log audit event
    log_audit_event(
        db,
        "LAB_RESULT_UPDATED",
        current_user.id,
        f"Updated lab result {lab_result.result_number}"
    )
    
    return lab_result


@router.post("/{result_id}/review", response_model=LabResultResponse)
async def review_lab_result(
    result_id: int,
    comments: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """Mark a lab result as reviewed by a doctor."""
    lab_result = db.query(LabResult).filter(LabResult.id == result_id).first()
    
    if not lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab result {result_id} not found"
        )
    
    if lab_result.status == LabResultStatus.REVIEWED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lab result already reviewed"
        )
    
    lab_result.status = LabResultStatus.REVIEWED
    lab_result.reviewed_date = datetime.utcnow()
    if comments:
        lab_result.doctor_comments = comments
    
    db.commit()
    db.refresh(lab_result)
    
    # Log audit event
    log_audit_event(
        db,
        "LAB_RESULT_REVIEWED",
        current_user.id,
        f"Reviewed lab result {lab_result.result_number}"
    )
    
    return lab_result


@router.get("/{result_id}/pdf")
async def generate_lab_result_pdf_endpoint(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a PDF for a lab result."""
    from app.utils.pdf_generator import generate_lab_result_pdf

    lab_result = db.query(LabResult).filter(LabResult.id == result_id).first()

    if not lab_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab result {result_id} not found"
        )

    # Get patient and doctor info
    patient = db.query(Patient).filter(Patient.id == lab_result.patient_id).first()
    doctor = db.query(User).filter(User.id == lab_result.doctor_id).first()

    # Prepare data for PDF
    pdf_data = {
        'result_number': lab_result.result_number,
        'test_date': lab_result.test_date.strftime('%B %d, %Y') if lab_result.test_date else 'N/A',
        'result_date': lab_result.result_date.strftime('%B %d, %Y') if lab_result.result_date else 'N/A',
        'patient_name': f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
        'doctor_name': doctor.username if doctor else "Unknown",
        'test_name': lab_result.test_name,
        'test_category': lab_result.test_category,
        'status': lab_result.status.value if lab_result.status else 'pending',
        'notes': lab_result.notes,
        'doctor_comments': lab_result.doctor_comments,
        'test_values': [
            {
                'parameter_name': val.parameter_name,
                'value': val.value,
                'reference_range': val.reference_range,
                'unit': val.unit
            }
            for val in lab_result.test_values
        ]
    }

    # Generate PDF
    pdf_buffer = generate_lab_result_pdf(pdf_data)

    # Log audit event
    log_audit_event(
        db,
        "LAB_RESULT_PDF_GENERATED",
        current_user.id,
        f"Generated PDF for lab result {lab_result.result_number}"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=lab_result_{result_id}.pdf"}
    )
