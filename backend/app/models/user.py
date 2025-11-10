from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
from .enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)  # Made optional for existing users
    full_name = Column(String, nullable=True)  # Added full name field
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, doctor, nurse, receptionist, accountant, pharmacist, lab_technician
    prc_license = Column(String, nullable=True)  # For doctors - Professional Regulation Commission license

    # Security fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_login = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        from .enums import has_permission, Permission
        try:
            user_role = UserRole(self.role)
            perm = Permission(permission)
            return has_permission(user_role, perm)
        except (ValueError, KeyError):
            return False
