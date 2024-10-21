"""
Pydantic schemas for lab results.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LabResultStatus(str, Enum):
    """Lab result status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class LabTestValueBase(BaseModel):
    """Base lab test value schema."""
    parameter_name: str = Field(..., min_length=2, max_length=200)
    value: str = Field(..., min_length=1, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    reference_range: Optional[str] = Field(None, max_length=100)
    is_abnormal: Optional[str] = Field(None, max_length=20)


class LabTestValueCreate(LabTestValueBase):
    """Schema for creating a lab test value."""
    pass


class LabTestValueResponse(LabTestValueBase):
    """Schema for lab test value response."""
    id: int
    lab_result_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LabResultBase(BaseModel):
    """Base lab result schema."""
    patient_id: int = Field(..., description="Patient ID")
    doctor_id: int = Field(..., description="Doctor ID")
    appointment_id: Optional[int] = Field(None, description="Related appointment ID")
    test_name: str = Field(..., min_length=2, max_length=200)
    test_category: Optional[str] = Field(None, max_length=100)
    test_date: datetime = Field(..., description="Date test was performed")
    notes: Optional[str] = Field(None, max_length=2000)


class LabResultCreate(LabResultBase):
    """Schema for creating a lab result."""
    test_values: List[LabTestValueCreate] = Field(..., min_items=1, description="Test values")


class LabResultUpdate(BaseModel):
    """Schema for updating a lab result."""
    status: Optional[LabResultStatus] = None
    result_date: Optional[datetime] = None
    reviewed_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)
    doctor_comments: Optional[str] = Field(None, max_length=2000)


class LabResultResponse(LabResultBase):
    """Schema for lab result response."""
    id: int
    result_number: str
    status: LabResultStatus
    result_date: Optional[datetime]
    reviewed_date: Optional[datetime]
    doctor_comments: Optional[str]
    created_at: datetime
    updated_at: datetime
    test_values: List[LabTestValueResponse]

    class Config:
        from_attributes = True


class LabResultWithDetails(LabResultResponse):
    """Lab result with patient and doctor details."""
    patient_name: str
    patient_email: str
    doctor_name: str


class LabResultListResponse(BaseModel):
    """Paginated lab result list response."""
    items: List[LabResultWithDetails]
    total: int
    page: int
    page_size: int
    total_pages: int

