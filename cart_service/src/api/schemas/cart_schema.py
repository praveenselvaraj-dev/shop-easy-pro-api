from pydantic import BaseModel

class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = 1

class UpdateCartRequest(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    price: float
    total: float
    name: str
    image: str

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: float
