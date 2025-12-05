from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from infrastructure.database.connection import Base
import enum
from sqlalchemy import Column, String, Integer, Float, DateTime, func
from uuid import uuid4
from datetime import datetime
class ProductTable(Base):
    __tablename__ = "product"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(String)
    image = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved = Column(Boolean, default=False)