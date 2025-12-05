from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str | None = None
    product_image: str | None = None
    quantity: int
    price: float


class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True