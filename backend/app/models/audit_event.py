from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base
import datetime

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(String) # e.g., 'CREATE', 'UPDATE', 'DELETE'
    user_id = Column(Integer, ForeignKey("users.id")) # Assuming you have a User model
    details = Column(String)

    user = relationship("User")
