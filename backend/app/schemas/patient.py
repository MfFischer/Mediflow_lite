"""
Pydantic schemas for Patient model.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum
import re


class GenderEnum(str, Enum):
    """Gender enum for API."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class PatientBase(BaseModel):
    """Base patient schema."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Optional[GenderEnum] = None
    email: EmailStr
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    address: Optional[str] = Field(None, max_length=500)
    ssn: Optional[str] = Field(None, max_length=20)
    insurance_number: Optional[str] = Field(None, max_length=100)
    medical_history: Optional[str] = None

    # Philippine Insurance Information
    philhealth_number: Optional[str] = Field(None, max_length=20, description="12-digit PhilHealth number")
    philhealth_member_type: Optional[str] = Field(None, max_length=50, description="Member, Dependent, Senior Citizen, PWD")
    hmo_provider: Optional[str] = Field(None, max_length=100, description="HMO provider name")
    hmo_card_number: Optional[str] = Field(None, max_length=100)
    hmo_coverage_limit: Optional[str] = Field(None, max_length=50, description="e.g., ₱100,000")
    hmo_validity_date: Optional[date] = None

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate that date of birth is not in the future."""
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v


class PatientCreate(PatientBase):
    """Schema for creating a new patient."""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    address: Optional[str] = Field(None, max_length=500)
    ssn: Optional[str] = Field(None, max_length=20)
    insurance_number: Optional[str] = Field(None, max_length=100)
    medical_history: Optional[str] = None

    # Philippine Insurance Information
    philhealth_number: Optional[str] = Field(None, max_length=20)
    philhealth_member_type: Optional[str] = Field(None, max_length=50)
    hmo_provider: Optional[str] = Field(None, max_length=100)
    hmo_card_number: Optional[str] = Field(None, max_length=100)
    hmo_coverage_limit: Optional[str] = Field(None, max_length=50)
    hmo_validity_date: Optional[date] = None

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate that date of birth is not in the future."""
        if v and v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v


class PatientResponse(PatientBase):
    """Schema for patient response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for paginated patient list response."""
    total: int
    page: int
    page_size: int
    patients: list[PatientResponse]

