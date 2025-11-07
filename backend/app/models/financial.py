"""
Financial management models for accounting and reporting.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status options."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """
    Payment tracking model.
    Tracks all payments received from patients.
    """
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Reference
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, card, bank_transfer, etc.
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.COMPLETED, nullable=False)
    
    # Transaction details
    reference_number = Column(String(100), nullable=True)  # Bank ref, card transaction ID, etc.
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice")
    patient = relationship("Patient")
    created_by_user = relationship("User")


class ExpenseCategory(str, enum.Enum):
    """Expense category options."""
    PHARMACY = "pharmacy"  # Medicine purchases
    MEDICAL_SUPPLIES = "medical_supplies"  # Syringes, gloves, etc.
    SALARIES = "salaries"  # Staff salaries
    UTILITIES = "utilities"  # Electricity, water, internet
    RENT = "rent"  # Building rent
    EQUIPMENT = "equipment"  # Medical equipment
    MAINTENANCE = "maintenance"  # Repairs and maintenance
    MARKETING = "marketing"  # Advertising
    PROFESSIONAL_FEES = "professional_fees"  # Doctor payouts
    TAXES = "taxes"  # BIR taxes
    INSURANCE = "insurance"  # Business insurance
    OTHER = "other"


class Expense(Base):
    """
    Expense tracking model.
    Tracks all business expenses.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Expense details
    category = Column(SQLEnum(ExpenseCategory), nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, nullable=False)
    
    # Vendor/Supplier
    vendor_name = Column(String(200), nullable=True)
    vendor_tin = Column(String(50), nullable=True)  # Tax Identification Number
    
    # Payment details
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # BIR compliance
    receipt_number = Column(String(100), nullable=True)
    is_vat_inclusive = Column(Integer, default=0)  # 0 = No, 1 = Yes
    vat_amount = Column(Float, default=0.0)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User")


class DoctorPayoutStatus(str, enum.Enum):
    """Doctor payout status."""
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class DoctorPayout(Base):
    """
    Doctor payout tracking.
    Tracks professional fees owed to doctors.
    """
    __tablename__ = "doctor_payouts"

    id = Column(Integer, primary_key=True, index=True)
    payout_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Doctor details
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_name = Column(String(200), nullable=False)
    doctor_license = Column(String(50), nullable=True)  # PRC License
    
    # Payout period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Financial details
    gross_amount = Column(Float, nullable=False)  # Total professional fees
    withholding_tax = Column(Float, default=0.0)  # BIR withholding tax (usually 10%)
    deductions = Column(Float, default=0.0)  # Other deductions
    net_amount = Column(Float, nullable=False)  # Amount to pay
    
    # Payment details
    status = Column(SQLEnum(DoctorPayoutStatus), default=DoctorPayoutStatus.PENDING, nullable=False)
    payment_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id])
    created_by_user = relationship("User", foreign_keys=[created_by])


class InventoryItem(Base):
    """
    Inventory tracking for pharmacy and medical supplies.
    """
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Item details
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)  # medicine, supplies, equipment
    
    # Stock details
    quantity = Column(Integer, nullable=False, default=0)
    unit = Column(String(50), nullable=False)  # pcs, box, bottle, etc.
    reorder_level = Column(Integer, default=10)  # Alert when stock is low
    
    # Pricing
    unit_cost = Column(Float, nullable=False)  # Purchase price
    selling_price = Column(Float, nullable=False)  # Selling price
    
    # Supplier
    supplier_name = Column(String(200), nullable=True)
    supplier_contact = Column(String(100), nullable=True)
    
    # Metadata
    expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InventoryTransaction(Base):
    """
    Inventory transaction log.
    Tracks all inventory movements (purchases, sales, adjustments).
    """
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Reference
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # purchase, sale, adjustment, return
    quantity = Column(Integer, nullable=False)  # Positive for in, negative for out
    unit_cost = Column(Float, nullable=True)
    
    # Reference documents
    reference_type = Column(String(50), nullable=True)  # invoice, expense, adjustment
    reference_id = Column(Integer, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("InventoryItem")
    created_by_user = relationship("User")


class BIRReport(Base):
    """
    BIR (Bureau of Internal Revenue) report tracking.
    Stores generated BIR reports for compliance.
    """
    __tablename__ = "bir_reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # Report details
    report_type = Column(String(100), nullable=False)  # sales_summary, vat_report, withholding_tax
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    
    # Financial summary
    total_sales = Column(Float, default=0.0)
    vat_amount = Column(Float, default=0.0)
    withholding_tax = Column(Float, default=0.0)
    
    # File storage
    file_path = Column(String(500), nullable=True)  # Path to generated PDF/Excel
    
    # Metadata
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    generated_by_user = relationship("User")

