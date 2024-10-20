from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import Optional
import math

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.audit_event import AuditEvent
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentWithDetails,
    AppointmentListResponse,
    AvailabilityRequest,
    AvailabilityResponse,
    TimeSlot
)


router = APIRouter()


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Helper to log audit events."""
    audit_event = AuditEvent(action=action, user_id=user_id, details=details)
    db.add(audit_event)
    db.commit()


@router.get("/", response_model=AppointmentListResponse)
async def list_appointments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List appointments with pagination and filtering."""
    query = db.query(Appointment)

    # Apply filters
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(Appointment.status == status)
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    appointments = query.order_by(Appointment.appointment_date.desc()).offset(offset).limit(page_size).all()

    # Build response with details
    items = []
    for apt in appointments:
        patient = db.query(Patient).filter(Patient.id == apt.patient_id).first()
        doctor = db.query(User).filter(User.id == apt.doctor_id).first()

        items.append(AppointmentWithDetails(
            id=apt.id,
            patient_id=apt.patient_id,
            doctor_id=apt.doctor_id,
            appointment_date=apt.appointment_date,
            duration_minutes=apt.duration_minutes,
            appointment_type=apt.appointment_type,
            reason=apt.reason,
            notes=apt.notes,
            status=apt.status,
            created_at=apt.created_at,
            updated_at=apt.updated_at,
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            patient_email=patient.email if patient else "",
            doctor_name=doctor.username if doctor else "Unknown",
            doctor_email=doctor.email if doctor else ""
        ))

    return AppointmentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )



@router.get("/{appointment_id}", response_model=AppointmentWithDetails)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific appointment by ID."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )

    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    doctor = db.query(User).filter(User.id == appointment.doctor_id).first()

    return AppointmentWithDetails(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        duration_minutes=appointment.duration_minutes,
        appointment_type=appointment.appointment_type,
        reason=appointment.reason,
        notes=appointment.notes,
        status=appointment.status,
        created_at=appointment.created_at,
        updated_at=appointment.updated_at,
        patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
        patient_email=patient.email if patient else "",
        doctor_name=doctor.username if doctor else "Unknown",
        doctor_email=doctor.email if doctor else ""
    )


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """Create a new appointment."""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == appointment_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {appointment_data.patient_id} not found"
        )

    # Verify doctor exists
    doctor = db.query(User).filter(User.id == appointment_data.doctor_id).first()
    if not doctor or doctor.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {appointment_data.doctor_id} not found"
        )

    # Check for scheduling conflicts
    end_time = appointment_data.appointment_date + timedelta(minutes=appointment_data.duration_minutes)

    conflicts = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == appointment_data.doctor_id,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            or_(
                # New appointment starts during existing appointment
                and_(
                    Appointment.appointment_date <= appointment_data.appointment_date,
                    Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) > appointment_data.appointment_date
                ),
                # New appointment ends during existing appointment
                and_(
                    Appointment.appointment_date < end_time,
                    Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) >= end_time
                ),
                # New appointment completely contains existing appointment
                and_(
                    Appointment.appointment_date >= appointment_data.appointment_date,
                    Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) <= end_time
                )
            )
        )
    ).first()

    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Doctor already has an appointment at this time"
        )

    # Create appointment
    new_appointment = Appointment(**appointment_data.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    # Log audit event
    log_audit_event(
        db,
        "APPOINTMENT_CREATED",
        current_user.id,
        f"Created appointment {new_appointment.id} for patient {patient.first_name} {patient.last_name}"
    )

    return new_appointment




@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """Update an existing appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )

    # Update fields
    update_data = appointment_data.model_dump(exclude_unset=True)

    # If updating appointment date, check for conflicts
    if "appointment_date" in update_data:
        duration = update_data.get("duration_minutes", appointment.duration_minutes)
        end_time = update_data["appointment_date"] + timedelta(minutes=duration)

        conflicts = db.query(Appointment).filter(
            and_(
                Appointment.id != appointment_id,
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                or_(
                    and_(
                        Appointment.appointment_date <= update_data["appointment_date"],
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) > update_data["appointment_date"]
                    ),
                    and_(
                        Appointment.appointment_date < end_time,
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) >= end_time
                    ),
                    and_(
                        Appointment.appointment_date >= update_data["appointment_date"],
                        Appointment.appointment_date + timedelta(minutes=Appointment.duration_minutes) <= end_time
                    )
                )
            )
        ).first()

        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Doctor already has an appointment at this time"
            )

    for key, value in update_data.items():
        setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)

    # Log audit event
    log_audit_event(
        db,
        "APPOINTMENT_UPDATED",
        current_user.id,
        f"Updated appointment {appointment_id}"
    )

    return appointment


@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """Delete an appointment (admin or doctor only)."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )

    db.delete(appointment)
    db.commit()

    # Log audit event
    log_audit_event(
        db,
        "APPOINTMENT_DELETED",
        current_user.id,
        f"Deleted appointment {appointment_id}"
    )

    return {"message": f"Appointment {appointment_id} deleted successfully"}


@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(
    request: AvailabilityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check doctor availability for a specific date.
    Returns available time slots.
    """
    # Verify doctor exists
    doctor = db.query(User).filter(User.id == request.doctor_id).first()
    if not doctor or doctor.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {request.doctor_id} not found"
        )

    # Define working hours (9 AM to 5 PM)
    start_hour = 9
    end_hour = 17

    # Get all appointments for the doctor on this date
    date_start = request.date.replace(hour=0, minute=0, second=0, microsecond=0)
    date_end = date_start + timedelta(days=1)

    appointments = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == request.doctor_id,
            Appointment.appointment_date >= date_start,
            Appointment.appointment_date < date_end,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        )
    ).order_by(Appointment.appointment_date).all()

    # Generate time slots
    slots = []
    current_time = date_start.replace(hour=start_hour)
    end_time = date_start.replace(hour=end_hour)

    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=request.duration_minutes)

        # Check if this slot conflicts with any appointment
        available = True
        for apt in appointments:
            apt_end = apt.appointment_date + timedelta(minutes=apt.duration_minutes)

            # Check for overlap
            if (current_time < apt_end and slot_end > apt.appointment_date):
                available = False
                break

        slots.append(TimeSlot(
            start_time=current_time,
            end_time=slot_end,
            available=available
        ))

        # Move to next slot (30-minute intervals)
        current_time += timedelta(minutes=30)

    return AvailabilityResponse(
        doctor_id=request.doctor_id,
        date=request.date,
        slots=slots
    )