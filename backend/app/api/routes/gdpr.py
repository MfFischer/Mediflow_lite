"""
GDPR compliance endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.gdpr import gdpr
from app.models.user import User

router = APIRouter()


@router.get("/export/{patient_id}")
async def export_patient_data(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "doctor"]))
):
    """
    Export all patient data (GDPR Right to Data Portability).
    
    Returns a JSON file with all patient information.
    """
    try:
        data = gdpr.export_patient_data(db, patient_id)
        return JSONResponse(
            content=data,
            headers={
                "Content-Disposition": f"attachment; filename=patient_{patient_id}_data.json"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/anonymize/{patient_id}")
async def anonymize_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Anonymize patient data (GDPR Right to be Forgotten).
    
    Only accessible by admin role.
    """
    try:
        gdpr.anonymize_patient_data(db, patient_id)
        return {
            "message": f"Patient {patient_id} data has been anonymized",
            "status": "success"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/consent/{patient_id}")
async def get_consent_status(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient consent status for data processing.
    """
    consent_info = gdpr.get_consent_status(db, patient_id)
    return consent_info


@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Delete data older than retention period.
    
    Only accessible by admin role.
    """
    deleted_count = gdpr.delete_old_data(db, days)
    return {
        "message": f"Deleted {deleted_count} old records",
        "deleted_count": deleted_count
    }

