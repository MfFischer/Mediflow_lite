"""
Enums for MediFlow Lite
Centralized enum definitions for consistent use across the application
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"  # Full system access
    DOCTOR = "doctor"  # Medical records, appointments, prescriptions
    NURSE = "nurse"  # Patient care, vital signs, medication administration
    RECEPTIONIST = "receptionist"  # Appointments, patient registration, billing
    ACCOUNTANT = "accountant"  # Financial reports, billing, payments
    PHARMACIST = "pharmacist"  # Pharmacy inventory, dispensing
    LAB_TECHNICIAN = "lab_technician"  # Laboratory tests and results


class Permission(str, Enum):
    """Granular permissions for RBAC"""
    # Patient Management
    PATIENT_CREATE = "patient:create"
    PATIENT_READ = "patient:read"
    PATIENT_UPDATE = "patient:update"
    PATIENT_DELETE = "patient:delete"
    
    # Appointment Management
    APPOINTMENT_CREATE = "appointment:create"
    APPOINTMENT_READ = "appointment:read"
    APPOINTMENT_UPDATE = "appointment:update"
    APPOINTMENT_DELETE = "appointment:delete"
    
    # Medical Records
    MEDICAL_RECORD_CREATE = "medical_record:create"
    MEDICAL_RECORD_READ = "medical_record:read"
    MEDICAL_RECORD_UPDATE = "medical_record:update"
    MEDICAL_RECORD_DELETE = "medical_record:delete"
    
    # Billing & Financial
    BILLING_CREATE = "billing:create"
    BILLING_READ = "billing:read"
    BILLING_UPDATE = "billing:update"
    BILLING_DELETE = "billing:delete"
    FINANCIAL_REPORTS = "financial:reports"
    
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # System Administration
    SYSTEM_SETTINGS = "system:settings"
    AUDIT_LOG_READ = "audit:read"
    BACKUP_MANAGE = "backup:manage"


# Role-Permission Mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        # Full access to everything
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE, Permission.PATIENT_DELETE,
        Permission.APPOINTMENT_CREATE, Permission.APPOINTMENT_READ, Permission.APPOINTMENT_UPDATE, Permission.APPOINTMENT_DELETE,
        Permission.MEDICAL_RECORD_CREATE, Permission.MEDICAL_RECORD_READ, Permission.MEDICAL_RECORD_UPDATE, Permission.MEDICAL_RECORD_DELETE,
        Permission.BILLING_CREATE, Permission.BILLING_READ, Permission.BILLING_UPDATE, Permission.BILLING_DELETE,
        Permission.FINANCIAL_REPORTS,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
        Permission.SYSTEM_SETTINGS, Permission.AUDIT_LOG_READ, Permission.BACKUP_MANAGE,
    ],
    
    UserRole.DOCTOR: [
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE,
        Permission.APPOINTMENT_CREATE, Permission.APPOINTMENT_READ, Permission.APPOINTMENT_UPDATE,
        Permission.MEDICAL_RECORD_CREATE, Permission.MEDICAL_RECORD_READ, Permission.MEDICAL_RECORD_UPDATE,
        Permission.BILLING_READ,  # Can view billing but not modify
    ],
    
    UserRole.NURSE: [
        Permission.PATIENT_READ, Permission.PATIENT_UPDATE,
        Permission.APPOINTMENT_READ,
        Permission.MEDICAL_RECORD_READ, Permission.MEDICAL_RECORD_UPDATE,
    ],
    
    UserRole.RECEPTIONIST: [
        Permission.PATIENT_CREATE, Permission.PATIENT_READ, Permission.PATIENT_UPDATE,
        Permission.APPOINTMENT_CREATE, Permission.APPOINTMENT_READ, Permission.APPOINTMENT_UPDATE, Permission.APPOINTMENT_DELETE,
        Permission.BILLING_CREATE, Permission.BILLING_READ, Permission.BILLING_UPDATE,
    ],
    
    UserRole.ACCOUNTANT: [
        Permission.PATIENT_READ,
        Permission.BILLING_CREATE, Permission.BILLING_READ, Permission.BILLING_UPDATE,
        Permission.FINANCIAL_REPORTS,
    ],
    
    UserRole.PHARMACIST: [
        Permission.PATIENT_READ,
        Permission.MEDICAL_RECORD_READ,  # To view prescriptions
        Permission.BILLING_CREATE, Permission.BILLING_READ,  # For pharmacy sales
    ],
    
    UserRole.LAB_TECHNICIAN: [
        Permission.PATIENT_READ,
        Permission.MEDICAL_RECORD_READ, Permission.MEDICAL_RECORD_UPDATE,  # For lab results
    ],
}


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(user_role, [])


def get_role_permissions(user_role: UserRole) -> list[Permission]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(user_role, [])

