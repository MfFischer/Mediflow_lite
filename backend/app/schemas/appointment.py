"""
Pydantic schemas for appointment management.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime, time
from typing import Optional
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status options."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Appointment type options."""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    ROUTINE_CHECKUP = "routine_checkup"
    VACCINATION = "vaccination"
    PROCEDURE = "procedure"
    TELEMEDICINE = "telemedicine"


class AppointmentBase(BaseModel):
    """Base appointment schema."""
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: int = Field(..., description="Doctor (user) ID")
    appointment_date: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(default=30, ge=15, le=240, description="Duration in minutes")
    appointment_type: AppointmentType = Field(default=AppointmentType.CONSULTATION)
    reason: str = Field(..., min_length=3, max_length=500, description="Reason for visit")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")
    status: AppointmentStatus = Field(default=AppointmentStatus.SCHEDULED)

    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """Ensure appointment is not in the past."""
        if v < datetime.utcnow():
            raise ValueError('Appointment date cannot be in the past')
        return v


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment."""
    pass


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment."""
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    appointment_type: Optional[AppointmentType] = None
    reason: Optional[str] = Field(None, min_length=3, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[AppointmentStatus] = None

    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        """Ensure appointment is not in the past."""
        if v and v < datetime.utcnow():
            raise ValueError('Appointment date cannot be in the past')
        return v


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentWithDetails(AppointmentResponse):
    """Appointment with patient and doctor details."""
    patient_name: str
    patient_email: str
    doctor_name: str
    doctor_email: str


class AppointmentListResponse(BaseModel):
    """Paginated appointment list response."""
    items: list[AppointmentWithDetails]
    total: int
    page: int
    page_size: int
    total_pages: int


class TimeSlot(BaseModel):
    """Available time slot."""
    start_time: datetime
    end_time: datetime
    available: bool


class AvailabilityRequest(BaseModel):
    """Request for checking availability."""
    doctor_id: int
    date: datetime
    duration_minutes: int = Field(default=30, ge=15, le=240)


class AvailabilityResponse(BaseModel):
    """Response with available time slots."""
    doctor_id: int
    date: datetime
    slots: list[TimeSlot]

