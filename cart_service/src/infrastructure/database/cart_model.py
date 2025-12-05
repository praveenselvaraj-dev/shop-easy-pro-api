from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .connection import Base
import uuid

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False) 
