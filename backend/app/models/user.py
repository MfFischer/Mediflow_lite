from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)  # Made optional for existing users
    full_name = Column(String, nullable=True)  # Added full name field
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, doctor, receptionist
    prc_license = Column(String, nullable=True)  # For doctors - Professional Regulation Commission license
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
