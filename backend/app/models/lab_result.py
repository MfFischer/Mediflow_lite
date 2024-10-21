"""
Lab results models.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class LabResultStatus(str, enum.Enum):
    """Lab result status options."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class LabResult(Base):
    """Lab result model."""
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, index=True)
    result_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Test details
    test_name = Column(String(200), nullable=False)
    test_category = Column(String(100), nullable=True)
    
    # Status
    status = Column(SQLEnum(LabResultStatus), default=LabResultStatus.PENDING, nullable=False)
    
    # Dates
    test_date = Column(DateTime, nullable=False)
    result_date = Column(DateTime, nullable=True)
    reviewed_date = Column(DateTime, nullable=True)
    
    # Results
    notes = Column(Text, nullable=True)
    doctor_comments = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient")
    doctor = relationship("User")
    appointment = relationship("Appointment")
    test_values = relationship("LabTestValue", back_populates="lab_result", cascade="all, delete-orphan")


class LabTestValue(Base):
    """Individual test values in a lab result."""
    __tablename__ = "lab_test_values"

    id = Column(Integer, primary_key=True, index=True)
    lab_result_id = Column(Integer, ForeignKey("lab_results.id"), nullable=False)
    
    # Test value details
    parameter_name = Column(String(200), nullable=False)
    value = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    is_abnormal = Column(String(20), nullable=True)  # "normal", "high", "low", "critical"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lab_result = relationship("LabResult", back_populates="test_values")

