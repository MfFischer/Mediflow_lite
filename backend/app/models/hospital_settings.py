"""
Hospital settings model for Philippine healthcare facilities.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from ..core.database import Base


class HospitalSettings(Base):
    """Hospital settings and information for invoices and documents."""
    __tablename__ = "hospital_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Hospital Information
    hospital_name = Column(String(200), nullable=False, default="Medical Center")
    hospital_address = Column(Text, nullable=True)
    hospital_phone = Column(String(50), nullable=True)
    hospital_email = Column(String(100), nullable=True)
    hospital_website = Column(String(200), nullable=True)
    
    # Legal Information
    doh_license_number = Column(String(100), nullable=True)  # DOH License
    tin = Column(String(50), nullable=True)  # Tax Identification Number
    philhealth_accreditation = Column(String(100), nullable=True)  # PhilHealth Accreditation Number
    
    # Branding
    logo_url = Column(String(500), nullable=True)  # Path to hospital logo
    
    # Invoice Settings
    invoice_prefix = Column(String(10), nullable=False, default="INV")
    invoice_footer = Column(Text, nullable=True)  # Payment terms, bank details, etc.
    authorized_signatory = Column(String(200), nullable=True)  # Name of person who signs invoices
    signatory_title = Column(String(100), nullable=True)  # e.g., "Hospital Administrator"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

