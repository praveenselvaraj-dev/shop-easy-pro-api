from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .connection import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String, index=True)      # admin user who performed action
    action = Column(String, index=True)     # e.g., "approve_product"
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
