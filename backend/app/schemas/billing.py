"""
Pydantic schemas for billing and invoicing.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status options."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Payment method options."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    INSURANCE = "insurance"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class InvoiceItemBase(BaseModel):
    """Base invoice item schema."""
    description: str = Field(..., min_length=3, max_length=500)
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    """Schema for creating an invoice item."""
    pass


class InvoiceItemResponse(InvoiceItemBase):
    """Schema for invoice item response."""
    id: int
    invoice_id: int
    total_price: float
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    """Base invoice schema."""
    patient_id: int = Field(..., description="Patient ID")
    appointment_id: Optional[int] = Field(None, description="Related appointment ID")
    notes: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""
    items: List[InvoiceItemCreate] = Field(..., min_items=1, description="Invoice line items")
    tax_rate: float = Field(default=0.0, ge=0, le=1, description="Tax rate (0-1)")
    discount_amount: float = Field(default=0.0, ge=0, description="Discount amount")


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice."""
    status: Optional[InvoiceStatus] = None
    payment_method: Optional[PaymentMethod] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response."""
    id: int
    invoice_number: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    status: InvoiceStatus
    payment_method: Optional[PaymentMethod]
    payment_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse]

    class Config:
        from_attributes = True


class InvoiceWithDetails(InvoiceResponse):
    """Invoice with patient details."""
    patient_name: str
    patient_email: str


class InvoiceListResponse(BaseModel):
    """Paginated invoice list response."""
    items: List[InvoiceWithDetails]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaymentRequest(BaseModel):
    """Request to record a payment."""
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class InvoiceSummary(BaseModel):
    """Summary of invoices for reporting."""
    total_invoices: int
    total_amount: float
    paid_amount: float
    pending_amount: float
    overdue_amount: float

