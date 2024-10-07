"""
GDPR compliance utilities.
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from .config import settings
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.audit_event import AuditEvent


class GDPRCompliance:
    """
    Handles GDPR compliance operations.
    """
    
    @staticmethod
    def export_patient_data(db: Session, patient_id: int) -> Dict[str, Any]:
        """
        Export all data for a patient (GDPR Right to Data Portability).
        
        Args:
            db: Database session
            patient_id: Patient ID
        
        Returns:
            Dictionary containing all patient data
        """
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Get all appointments
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).all()
        
        # Get audit events related to this patient
        audit_events = db.query(AuditEvent).filter(
            AuditEvent.details.like(f"%patient {patient.first_name} {patient.last_name}%")
        ).all()
        
        return {
            "export_date": datetime.utcnow().isoformat(),
            "patient": {
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "date_of_birth": patient.date_of_birth.isoformat(),
                "email": patient.email,
                "phone_number": patient.phone_number,
            },
            "appointments": [
                {
                    "id": apt.id,
                    "date": apt.appointment_date.isoformat(),
                    "reason": apt.reason,
                }
                for apt in appointments
            ],
            "audit_trail": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "action": event.action,
                    "details": event.details,
                }
                for event in audit_events
            ],
        }
    
    @staticmethod
    def anonymize_patient_data(db: Session, patient_id: int) -> None:
        """
        Anonymize patient data (GDPR Right to be Forgotten).
        
        Replaces personal data with anonymized values while preserving
        statistical integrity.
        
        Args:
            db: Database session
            patient_id: Patient ID
        """
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Anonymize patient data
        patient.first_name = f"DELETED_{patient_id}"
        patient.last_name = "USER"
        patient.email = f"deleted_{patient_id}@anonymized.local"
        patient.phone_number = "+00000000000"
        
        # Note: We keep date_of_birth for statistical purposes (age distribution)
        # but it's anonymized by removing the link to the person
        
        db.commit()
        
        # Log the anonymization
        audit_event = AuditEvent(
            action="PATIENT_ANONYMIZED",
            user_id=None,  # System action
            details=f"Patient {patient_id} data anonymized per GDPR request"
        )
        db.add(audit_event)
        db.commit()
    
    @staticmethod
    def delete_old_data(db: Session, days: int = None) -> int:
        """
        Delete data older than retention period (GDPR Data Minimization).
        
        Args:
            db: Database session
            days: Number of days to retain (default from settings)
        
        Returns:
            Number of records deleted
        """
        retention_days = days or settings.data_retention_days
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Delete old audit events
        deleted_count = db.query(AuditEvent).filter(
            AuditEvent.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        
        return deleted_count
    
    @staticmethod
    def get_consent_status(db: Session, patient_id: int) -> Dict[str, Any]:
        """
        Get patient consent status for data processing.
        
        Args:
            db: Database session
            patient_id: Patient ID
        
        Returns:
            Dictionary with consent information
        """
        # This is a placeholder - in production, you'd have a Consent model
        return {
            "patient_id": patient_id,
            "data_processing_consent": True,
            "marketing_consent": False,
            "research_consent": False,
            "consent_date": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def record_data_breach(
        db: Session,
        description: str,
        affected_records: int,
        severity: str
    ) -> None:
        """
        Record a data breach incident (GDPR Breach Notification).
        
        Args:
            db: Database session
            description: Description of the breach
            affected_records: Number of records affected
            severity: Severity level (low, medium, high, critical)
        """
        audit_event = AuditEvent(
            action="DATA_BREACH",
            user_id=None,
            details=json.dumps({
                "description": description,
                "affected_records": affected_records,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
            })
        )
        db.add(audit_event)
        db.commit()
        
        # In production, this should trigger:
        # 1. Notification to Data Protection Officer
        # 2. Email to affected users (if required)
        # 3. Notification to supervisory authority (within 72 hours if required)


# Global GDPR compliance instance
gdpr = GDPRCompliance()

