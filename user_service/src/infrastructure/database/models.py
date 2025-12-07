from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from src.infrastructure.database.connection import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserModel(Base):
    """SQLAlchemy User Model"""
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}  # ✅ add this
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)  
    email = Column(String(255), unique=True, index=True, nullable=False)     
    password_hash = Column(String(255), nullable=False)                      
    role = Column(String(50), default="user", nullable=False)               
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
