"""
Financial management and reporting API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, date, timedelta
from typing import Optional, List
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.billing import Invoice, InvoiceItem, InvoiceStatus, ItemCategory
from app.models.financial import (
    Payment, Expense, DoctorPayout, InventoryItem, 
    ExpenseCategory, DoctorPayoutStatus
)

router = APIRouter(prefix="/financial", tags=["Financial Management"])


# ==================== REVENUE REPORTS ====================

@router.get("/revenue/summary")
async def get_revenue_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get revenue summary for a period.
    Shows total revenue, payment methods breakdown, and category breakdown.
    """
    # Default to current month if no dates provided
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Total revenue (paid invoices)
    total_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).scalar() or 0.0
    
    # Revenue by payment method
    payment_methods = db.query(
        Invoice.payment_method,
        func.sum(Invoice.total_amount).label('amount'),
        func.count(Invoice.id).label('count')
    ).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).group_by(Invoice.payment_method).all()
    
    # Revenue by category
    category_revenue = db.query(
        InvoiceItem.category,
        func.sum(InvoiceItem.total_price).label('amount')
    ).join(Invoice).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).group_by(InvoiceItem.category).all()
    
    # Insurance coverage breakdown
    philhealth_total = db.query(func.sum(Invoice.philhealth_coverage)).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).scalar() or 0.0
    
    hmo_total = db.query(func.sum(Invoice.hmo_coverage)).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).scalar() or 0.0
    
    senior_pwd_total = db.query(func.sum(Invoice.senior_pwd_discount)).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).scalar() or 0.0
    
    # Number of transactions
    transaction_count = db.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).scalar() or 0
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_revenue": float(total_revenue),
            "transaction_count": transaction_count,
            "average_transaction": float(total_revenue / transaction_count) if transaction_count > 0 else 0.0
        },
        "payment_methods": [
            {
                "method": pm[0],
                "amount": float(pm[1]),
                "count": pm[2],
                "percentage": float(pm[1] / total_revenue * 100) if total_revenue > 0 else 0.0
            }
            for pm in payment_methods
        ],
        "category_breakdown": [
            {
                "category": cat[0],
                "amount": float(cat[1]),
                "percentage": float(cat[1] / total_revenue * 100) if total_revenue > 0 else 0.0
            }
            for cat in category_revenue
        ],
        "insurance_coverage": {
            "philhealth": float(philhealth_total),
            "hmo": float(hmo_total),
            "senior_pwd_discount": float(senior_pwd_total),
            "total_coverage": float(philhealth_total + hmo_total + senior_pwd_total)
        }
    }


@router.get("/revenue/daily")
async def get_daily_revenue(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily revenue breakdown.
    Useful for charts and trend analysis.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    daily_revenue = db.query(
        func.date(Invoice.payment_date).label('date'),
        func.sum(Invoice.total_amount).label('revenue'),
        func.count(Invoice.id).label('transactions')
    ).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).group_by(func.date(Invoice.payment_date)).order_by(func.date(Invoice.payment_date)).all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "daily_data": [
            {
                "date": str(day[0]),
                "revenue": float(day[1]),
                "transactions": day[2]
            }
            for day in daily_revenue
        ]
    }


# ==================== EXPENSE REPORTS ====================

@router.get("/expenses/summary")
async def get_expense_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get expense summary for a period.
    Shows total expenses and category breakdown.
    """
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Total expenses
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).scalar() or 0.0
    
    # Expenses by category
    category_expenses = db.query(
        Expense.category,
        func.sum(Expense.amount).label('amount'),
        func.count(Expense.id).label('count')
    ).filter(
        and_(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).group_by(Expense.category).all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_expenses": float(total_expenses),
            "transaction_count": sum(cat[2] for cat in category_expenses)
        },
        "category_breakdown": [
            {
                "category": cat[0],
                "amount": float(cat[1]),
                "count": cat[2],
                "percentage": float(cat[1] / total_expenses * 100) if total_expenses > 0 else 0.0
            }
            for cat in category_expenses
        ]
    }


# ==================== PROFITABILITY ====================

@router.get("/profitability")
async def get_profitability(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get profitability analysis.
    Revenue - Expenses = Profit
    """
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Total revenue
    total_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        and_(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date
        )
    ).scalar() or 0.0
    
    # Total expenses
    total_expenses = db.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).scalar() or 0.0
    
    # Calculate profit
    gross_profit = total_revenue - total_expenses
    profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "revenue": float(total_revenue),
        "expenses": float(total_expenses),
        "gross_profit": float(gross_profit),
        "profit_margin_percent": float(profit_margin)
    }


# ==================== DOCTOR PAYOUTS ====================

@router.get("/doctor-payouts/summary")
async def get_doctor_payout_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get doctor payout summary.
    Shows professional fees earned by each doctor.
    """
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Professional fees by doctor
    doctor_fees = db.query(
        InvoiceItem.doctor_name,
        InvoiceItem.doctor_license,
        func.sum(InvoiceItem.total_price).label('total_fees'),
        func.count(InvoiceItem.id).label('transaction_count')
    ).join(Invoice).filter(
        and_(
            InvoiceItem.category == ItemCategory.PROFESSIONAL_FEE,
            Invoice.status == InvoiceStatus.PAID,
            Invoice.payment_date >= start_date,
            Invoice.payment_date <= end_date,
            InvoiceItem.doctor_name.isnot(None)
        )
    ).group_by(InvoiceItem.doctor_name, InvoiceItem.doctor_license).all()
    
    total_professional_fees = sum(float(doc[2]) for doc in doctor_fees)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_professional_fees": float(total_professional_fees),
            "doctor_count": len(doctor_fees)
        },
        "doctors": [
            {
                "doctor_name": doc[0],
                "doctor_license": doc[1],
                "total_fees": float(doc[2]),
                "transaction_count": doc[3],
                "percentage": float(doc[2] / total_professional_fees * 100) if total_professional_fees > 0 else 0.0
            }
            for doc in doctor_fees
        ]
    }


# ==================== ACCOUNTS RECEIVABLE ====================

@router.get("/accounts-receivable")
async def get_accounts_receivable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get accounts receivable summary.
    Shows outstanding balances from patients.
    """
    # Pending invoices
    pending = db.query(func.sum(Invoice.patient_balance)).filter(
        Invoice.status == InvoiceStatus.PENDING
    ).scalar() or 0.0
    
    # Overdue invoices
    overdue = db.query(func.sum(Invoice.patient_balance)).filter(
        Invoice.status == InvoiceStatus.OVERDUE
    ).scalar() or 0.0
    
    # Count
    pending_count = db.query(func.count(Invoice.id)).filter(
        Invoice.status == InvoiceStatus.PENDING
    ).scalar() or 0
    
    overdue_count = db.query(func.count(Invoice.id)).filter(
        Invoice.status == InvoiceStatus.OVERDUE
    ).scalar() or 0
    
    return {
        "total_receivable": float(pending + overdue),
        "pending": {
            "amount": float(pending),
            "count": pending_count
        },
        "overdue": {
            "amount": float(overdue),
            "count": overdue_count
        }
    }

