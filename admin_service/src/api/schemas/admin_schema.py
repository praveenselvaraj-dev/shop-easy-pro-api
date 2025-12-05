from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    price: float

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

class PagedOrders(BaseModel):
    total: int
    page: int
    size: int
    items: List[OrderResponse]

class LowStockItem(BaseModel):
    product_id: str
    name: str
    stock: int

class SalesSummary(BaseModel):
    total_sales: float
    total_orders: int
    from_date: str | None
    to_date: str | None

class ApproveRequest(BaseModel):
    entity: str     
    entity_id: str
    approve: bool

class AuditLogResponse(BaseModel):
    id: int
    actor: str
    action: str
    details: str
    created_at: datetime
