"""
Pydantic schemas for hospital settings.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class HospitalSettingsBase(BaseModel):
    """Base hospital settings schema."""
    hospital_name: str = Field(..., min_length=1, max_length=200)
    hospital_address: Optional[str] = None
    hospital_phone: Optional[str] = Field(None, max_length=50)
    hospital_email: Optional[EmailStr] = None
    hospital_website: Optional[str] = Field(None, max_length=200)
    
    doh_license_number: Optional[str] = Field(None, max_length=100, description="DOH License Number")
    tin: Optional[str] = Field(None, max_length=50, description="Tax Identification Number")
    philhealth_accreditation: Optional[str] = Field(None, max_length=100, description="PhilHealth Accreditation")
    
    logo_url: Optional[str] = Field(None, max_length=500)
    
    invoice_prefix: str = Field(default="INV", max_length=10)
    invoice_footer: Optional[str] = Field(None, description="Payment terms, bank details")
    authorized_signatory: Optional[str] = Field(None, max_length=200)
    signatory_title: Optional[str] = Field(None, max_length=100)


class HospitalSettingsCreate(HospitalSettingsBase):
    """Schema for creating hospital settings."""
    pass


class HospitalSettingsUpdate(BaseModel):
    """Schema for updating hospital settings."""
    hospital_name: Optional[str] = Field(None, min_length=1, max_length=200)
    hospital_address: Optional[str] = None
    hospital_phone: Optional[str] = Field(None, max_length=50)
    hospital_email: Optional[EmailStr] = None
    hospital_website: Optional[str] = Field(None, max_length=200)
    
    doh_license_number: Optional[str] = Field(None, max_length=100)
    tin: Optional[str] = Field(None, max_length=50)
    philhealth_accreditation: Optional[str] = Field(None, max_length=100)
    
    logo_url: Optional[str] = Field(None, max_length=500)
    
    invoice_prefix: Optional[str] = Field(None, max_length=10)
    invoice_footer: Optional[str] = None
    authorized_signatory: Optional[str] = Field(None, max_length=200)
    signatory_title: Optional[str] = Field(None, max_length=100)


class HospitalSettingsResponse(HospitalSettingsBase):
    """Schema for hospital settings response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

