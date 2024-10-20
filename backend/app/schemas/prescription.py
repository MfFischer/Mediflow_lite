"""
Pydantic schemas for e-prescriptions.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class MedicationBase(BaseModel):
    """Base medication schema."""
    medication_name: str = Field(..., min_length=2, max_length=200)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    duration: str = Field(..., min_length=1, max_length=100)
    instructions: Optional[str] = Field(None, max_length=1000)


class MedicationCreate(MedicationBase):
    """Schema for creating a medication."""
    pass


class MedicationResponse(MedicationBase):
    """Schema for medication response."""
    id: int
    prescription_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PrescriptionBase(BaseModel):
    """Base prescription schema."""
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: int = Field(..., description="Doctor ID")
    appointment_id: Optional[int] = Field(None, description="Related appointment ID")
    diagnosis: str = Field(..., min_length=3, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)


class PrescriptionCreate(PrescriptionBase):
    """Schema for creating a prescription."""
    medications: List[MedicationCreate] = Field(..., min_items=1, description="List of medications")


class PrescriptionUpdate(BaseModel):
    """Schema for updating a prescription."""
    diagnosis: Optional[str] = Field(None, min_length=3, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    dispensed: Optional[bool] = None
    dispensed_date: Optional[datetime] = None


class PrescriptionResponse(PrescriptionBase):
    """Schema for prescription response."""
    id: int
    prescription_number: str
    is_active: bool
    dispensed: bool
    dispensed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    medications: List[MedicationResponse]

    class Config:
        from_attributes = True


class PrescriptionWithDetails(PrescriptionResponse):
    """Prescription with patient and doctor details."""
    patient_name: str
    patient_email: str
    doctor_name: str


class PrescriptionListResponse(BaseModel):
    """Paginated prescription list response."""
    items: List[PrescriptionWithDetails]
    total: int
    page: int
    page_size: int
    total_pages: int

