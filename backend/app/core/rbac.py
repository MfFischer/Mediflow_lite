"""
Role-Based Access Control (RBAC) for MediFlow Lite
Provides decorators and dependencies for permission checking
"""
from functools import wraps
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..models.enums import UserRole, Permission, has_permission
from .security import get_current_user
from .database import get_db


class PermissionDenied(HTTPException):
    """Custom exception for permission denied"""
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def require_role(allowed_roles: List[UserRole]):
    """
    Dependency to check if user has one of the allowed roles
    
    Usage:
        @router.get("/admin/users")
        async def get_users(current_user: User = Depends(require_role([UserRole.ADMIN]))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise PermissionDenied(f"Invalid role: {current_user.role}")
        
        if user_role not in allowed_roles:
            role_names = ", ".join([role.value for role in allowed_roles])
            raise PermissionDenied(
                f"This action requires one of these roles: {role_names}. Your role: {user_role.value}"
            )
        
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive. Please contact administrator."
            )
        
        if current_user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is locked due to multiple failed login attempts. Please contact administrator."
            )
        
        return current_user
    
    return role_checker


def require_permission(required_permission: Permission):
    """
    Dependency to check if user has a specific permission
    
    Usage:
        @router.delete("/patients/{patient_id}")
        async def delete_patient(
            patient_id: int,
            current_user: User = Depends(require_permission(Permission.PATIENT_DELETE))
        ):
            ...
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise PermissionDenied(f"Invalid role: {current_user.role}")
        
        if not has_permission(user_role, required_permission):
            raise PermissionDenied(
                f"This action requires permission: {required_permission.value}. Your role ({user_role.value}) doesn't have this permission."
            )
        
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive. Please contact administrator."
            )
        
        if current_user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is locked. Please contact administrator."
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(required_permissions: List[Permission]):
    """
    Dependency to check if user has ANY of the specified permissions
    
    Usage:
        @router.get("/billing")
        async def get_billing(
            current_user: User = Depends(require_any_permission([
                Permission.BILLING_READ,
                Permission.FINANCIAL_REPORTS
            ]))
        ):
            ...
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise PermissionDenied(f"Invalid role: {current_user.role}")
        
        has_any = any(has_permission(user_role, perm) for perm in required_permissions)
        
        if not has_any:
            perm_names = ", ".join([perm.value for perm in required_permissions])
            raise PermissionDenied(
                f"This action requires one of these permissions: {perm_names}"
            )
        
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive. Please contact administrator."
            )
        
        if current_user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is locked. Please contact administrator."
            )
        
        return current_user
    
    return permission_checker


def require_all_permissions(required_permissions: List[Permission]):
    """
    Dependency to check if user has ALL of the specified permissions
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        try:
            user_role = UserRole(current_user.role)
        except ValueError:
            raise PermissionDenied(f"Invalid role: {current_user.role}")
        
        has_all = all(has_permission(user_role, perm) for perm in required_permissions)
        
        if not has_all:
            perm_names = ", ".join([perm.value for perm in required_permissions])
            raise PermissionDenied(
                f"This action requires ALL of these permissions: {perm_names}"
            )
        
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive. Please contact administrator."
            )
        
        if current_user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is locked. Please contact administrator."
            )
        
        return current_user
    
    return permission_checker


# Convenience dependencies for common role combinations
require_admin = require_role([UserRole.ADMIN])
require_doctor = require_role([UserRole.DOCTOR])
require_nurse = require_role([UserRole.NURSE])
require_receptionist = require_role([UserRole.RECEPTIONIST])
require_accountant = require_role([UserRole.ACCOUNTANT])

# Medical staff (doctors and nurses)
require_medical_staff = require_role([UserRole.DOCTOR, UserRole.NURSE])

# Financial staff (accountants and receptionists)
require_financial_staff = require_role([UserRole.ACCOUNTANT, UserRole.RECEPTIONIST, UserRole.ADMIN])

# Administrative staff (admin and receptionist)
require_admin_staff = require_role([UserRole.ADMIN, UserRole.RECEPTIONIST])

