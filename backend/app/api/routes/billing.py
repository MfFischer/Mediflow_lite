from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import math
import random
import string

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.billing import Invoice, InvoiceItem, InvoiceStatus, PaymentMethod
from app.models.patient import Patient
from app.models.audit_event import AuditEvent
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceWithDetails,
    InvoiceListResponse,
    PaymentRequest,
    InvoiceSummary
)


router = APIRouter()


def generate_invoice_number() -> str:
    """Generate a unique invoice number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"INV-{timestamp}-{random_suffix}"


def log_audit_event(db: Session, action: str, user_id: int, details: str):
    """Helper to log audit events."""
    audit_event = AuditEvent(action=action, user_id=user_id, details=details)
    db.add(audit_event)
    db.commit()


@router.get("/", response_model=InvoiceListResponse)
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[int] = None,
    status: Optional[InvoiceStatus] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List invoices with pagination and filtering."""
    query = db.query(Invoice)

    # Apply filters
    if patient_id:
        query = query.filter(Invoice.patient_id == patient_id)
    if status:
        query = query.filter(Invoice.status == status)
    if date_from:
        query = query.filter(Invoice.created_at >= date_from)
    if date_to:
        query = query.filter(Invoice.created_at <= date_to)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    invoices = query.order_by(Invoice.created_at.desc()).offset(offset).limit(page_size).all()

    # Build response with details
    items = []
    for inv in invoices:
        patient = db.query(Patient).filter(Patient.id == inv.patient_id).first()

        items.append(InvoiceWithDetails(
            id=inv.id,
            invoice_number=inv.invoice_number,
            patient_id=inv.patient_id,
            appointment_id=inv.appointment_id,
            subtotal=inv.subtotal,
            tax_amount=inv.tax_amount,
            discount_amount=inv.discount_amount,
            total_amount=inv.total_amount,
            status=inv.status,
            payment_method=inv.payment_method,
            payment_date=inv.payment_date,
            notes=inv.notes,
            due_date=inv.due_date,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
            items=[item for item in inv.items],
            patient_name=f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            patient_email=patient.email if patient else ""
        ))

    return InvoiceListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )



@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific invoice by ID."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    return invoice


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """Create a new invoice."""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == invoice_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {invoice_data.patient_id} not found"
        )

    # Calculate totals
    subtotal = sum(item.quantity * item.unit_price for item in invoice_data.items)
    tax_amount = subtotal * invoice_data.tax_rate
    discount_amount = invoice_data.discount_amount
    total_amount = subtotal + tax_amount - discount_amount

    # Create invoice
    new_invoice = Invoice(
        invoice_number=generate_invoice_number(),
        patient_id=invoice_data.patient_id,
        appointment_id=invoice_data.appointment_id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        notes=invoice_data.notes,
        due_date=invoice_data.due_date,
        status=InvoiceStatus.PENDING
    )

    db.add(new_invoice)
    db.flush()  # Get the invoice ID

    # Create invoice items
    for item_data in invoice_data.items:
        item = InvoiceItem(
            invoice_id=new_invoice.id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.quantity * item_data.unit_price
        )
        db.add(item)

    db.commit()
    db.refresh(new_invoice)

    # Log audit event
    log_audit_event(
        db,
        "INVOICE_CREATED",
        current_user.id,
        f"Created invoice {new_invoice.invoice_number} for patient {patient.first_name} {patient.last_name}"
    )

    return new_invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor", "receptionist"]))
):
    """Update an existing invoice."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    # Update fields
    update_data = invoice_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(invoice, key, value)

    db.commit()
    db.refresh(invoice)

    # Log audit event
    log_audit_event(
        db,
        "INVOICE_UPDATED",
        current_user.id,
        f"Updated invoice {invoice.invoice_number}"
    )

    return invoice


@router.post("/{invoice_id}/payment", response_model=InvoiceResponse)
async def record_payment(
    invoice_id: int,
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "receptionist"]))
):
    """Record a payment for an invoice."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    if invoice.status == InvoiceStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice is already paid"
        )

    # Update invoice
    invoice.status = InvoiceStatus.PAID
    invoice.payment_method = payment_data.payment_method
    invoice.payment_date = payment_data.payment_date or datetime.utcnow()
    if payment_data.notes:
        invoice.notes = f"{invoice.notes}\n\nPayment: {payment_data.notes}" if invoice.notes else f"Payment: {payment_data.notes}"

    db.commit()
    db.refresh(invoice)

    # Log audit event
    log_audit_event(
        db,
        "PAYMENT_RECORDED",
        current_user.id,
        f"Recorded payment for invoice {invoice.invoice_number} - {payment_data.payment_method.value}"
    )

    return invoice


@router.get("/{invoice_id}/pdf")
async def generate_invoice_pdf_endpoint(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a PDF for an invoice."""
    from app.utils.pdf_generator import generate_invoice_pdf

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found"
        )

    # Get patient info
    patient = db.query(Patient).filter(Patient.id == invoice.patient_id).first()

    # Prepare data for PDF
    pdf_data = {
        'invoice_number': invoice.invoice_number,
        'due_date': invoice.due_date.strftime('%B %d, %Y') if invoice.due_date else 'N/A',
        'patient_name': f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
        'status': invoice.status.value if invoice.status else 'pending',
        'subtotal': float(invoice.subtotal),
        'tax_amount': float(invoice.tax_amount),
        'discount_amount': float(invoice.discount_amount),
        'total_amount': float(invoice.total_amount),
        'payment_date': invoice.payment_date.strftime('%B %d, %Y') if invoice.payment_date else None,
        'payment_method': invoice.payment_method.value if invoice.payment_method else None,
        'notes': invoice.notes,
        'items': [
            {
                'description': item.description,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'amount': float(item.amount)
            }
            for item in invoice.items
        ]
    }

    # Generate PDF
    pdf_buffer = generate_invoice_pdf(pdf_data)

    # Log audit event
    log_audit_event(
        db,
        "INVOICE_PDF_GENERATED",
        current_user.id,
        f"Generated PDF for invoice {invoice.invoice_number}"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"}
    )


@router.get("/summary/stats", response_model=InvoiceSummary)
async def get_invoice_summary(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """Get invoice summary statistics."""
    query = db.query(Invoice)

    if date_from:
        query = query.filter(Invoice.created_at >= date_from)
    if date_to:
        query = query.filter(Invoice.created_at <= date_to)

    invoices = query.all()

    total_invoices = len(invoices)
    total_amount = sum(inv.total_amount for inv in invoices)
    paid_amount = sum(inv.total_amount for inv in invoices if inv.status == InvoiceStatus.PAID)
    pending_amount = sum(inv.total_amount for inv in invoices if inv.status == InvoiceStatus.PENDING)
    overdue_amount = sum(inv.total_amount for inv in invoices if inv.status == InvoiceStatus.OVERDUE)

    return InvoiceSummary(
        total_invoices=total_invoices,
        total_amount=total_amount,
        paid_amount=paid_amount,
        pending_amount=pending_amount,
        overdue_amount=overdue_amount
    )