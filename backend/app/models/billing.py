"""
Billing and invoice models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice status options."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method options."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    INSURANCE = "insurance"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class Invoice(Base):
    """Invoice model for billing."""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Financial details
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)

    # Philippine Insurance Coverage
    philhealth_coverage = Column(Float, nullable=False, default=0.0)
    hmo_coverage = Column(Float, nullable=False, default=0.0)
    senior_pwd_discount = Column(Float, nullable=False, default=0.0)  # 20% discount for Senior/PWD

    total_amount = Column(Float, nullable=False, default=0.0)
    patient_balance = Column(Float, nullable=False, default=0.0)  # Amount patient needs to pay
    
    # Payment details
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    payment_date = Column(DateTime, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="invoices")
    appointment = relationship("Appointment")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class ItemCategory(str, enum.Enum):
    """Invoice item category for Philippine hospitals."""
    PROFESSIONAL_FEE = "professional_fee"  # Doctor's fee
    LABORATORY = "laboratory"  # Lab tests
    MEDICATION = "medication"  # Medicines
    ROOM_CHARGE = "room_charge"  # Hospital room
    PROCEDURE = "procedure"  # Medical procedures
    SUPPLIES = "supplies"  # Medical supplies
    OTHER = "other"


class InvoiceItem(Base):
    """Individual line items in an invoice."""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)

    description = Column(String(500), nullable=False)
    category = Column(SQLEnum(ItemCategory), default=ItemCategory.OTHER, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # For professional fees - link to doctor
    doctor_name = Column(String(200), nullable=True)
    doctor_license = Column(String(50), nullable=True)  # PRC License Number

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")

