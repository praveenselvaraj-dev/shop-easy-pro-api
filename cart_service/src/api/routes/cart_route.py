from fastapi import APIRouter, Depends
from common_auth.dependencies import get_current_user, get_raw_token
from api.schemas.cart_schema import AddToCartRequest, UpdateCartRequest, CartResponse, CartItemResponse
from domain.services.cart_service import CartService
from infrastructure.repositories.cart_repository_Impl import CartRepositoryImpl
from infrastructure.database.connection import get_db
from utils.exceptions import (
    ProductNotFoundError, NotEnoughStockError, CartItemNotFoundError, ForbiddenError
)

from infrastructure.cache.redis_client import cache_get, cache_set, cache_delete

router = APIRouter()
PRODUCT_SERVICE_URL = "http://127.0.0.1:8001/api/v1/Product"


def get_service(db=Depends(get_db)):
    return CartService(CartRepositoryImpl(db))


@router.get("/", response_model=CartResponse)
def get_cart(user=Depends(get_current_user), token=Depends(get_raw_token), service=Depends(get_service)):
    user_id = user["sub"]
    items = service.get_cart(user_id)
    response_items = []

    for i in items:
        product = service.fetch_product_details(i.product_id, token)
        if not product:
            raise ProductNotFoundError(f"Product {i.product_id} not found")

        response_items.append({
            "id": i.id,
            "product_id": i.product_id,
            "quantity": i.quantity,
            "price": i.price,
            "total": i.price * i.quantity,
            "name": product["name"],
            "image": product["image"]
        })

    return {
        "items": response_items,
        "total": sum(i.price * i.quantity for i in items)
    }


@router.post("/", response_model=CartItemResponse)
def add_to_cart(request: AddToCartRequest, user=Depends(get_current_user), token=Depends(get_raw_token), service=Depends(get_service)):
    user_id = user["sub"]
    item = service.add_to_cart(user_id, request.product_id, request.quantity, token)

    product = service.fetch_product_details(item.product_id, token)
    if not product:
        raise ProductNotFoundError(f"Product {item.product_id} not found")

    return {
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "price": item.price,
        "total": item.quantity * item.price,
        "name": product["name"],
        "image": product["image"]
    }


@router.put("/{item_id}")
def update_quantity(item_id: str, request: UpdateCartRequest, user=Depends(get_current_user), token=Depends(get_raw_token), service=Depends(get_service)):
    item = service.update_quantity(item_id, request.quantity, user["sub"], token)
    if not item:
        raise CartItemNotFoundError(f"Cart item {item_id} not found")

    product = service.fetch_product_details(item.product_id, token)
    if not product:
        raise ProductNotFoundError(f"Product {item.product_id} not found")

    return {
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "price": item.price,
        "total": item.price * item.quantity,
        "name": product["name"],
        "image": product["image"]
    }


@router.delete("/{item_id}")
def remove_item(item_id: str, user=Depends(get_current_user), token=Depends(get_raw_token), service=Depends(get_service)):
    success = service.delete_item(item_id, user["sub"], token)
    if not success:
        raise CartItemNotFoundError(f"Cart item {item_id} not found")
    return {"message": "Item removed successfully"}


@router.delete("/")
def clear_cart(user=Depends(get_current_user), token=Depends(get_raw_token), service=Depends(get_service)):
    service.clear_cart(user["sub"], token)
    return {"message": "Cart cleared successfully"}
