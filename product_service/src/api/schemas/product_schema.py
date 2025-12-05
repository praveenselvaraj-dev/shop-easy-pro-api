from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProductCreateRequest(BaseModel):
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str] = None

class ProductUpdateRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    stock: Optional[int]
    category: Optional[str]

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    image: Optional[str]
    approved: bool

    class Config:
        orm_mode = True

class PaginatedProductResponse(BaseModel):
    total: int
    page: int
    size: int
    products: List[ProductResponse]
