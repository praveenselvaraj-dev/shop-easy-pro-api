from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas.order_schema import OrderResponse
from src.domain.services.order_service import OrderService
from src.infrastructure.repositories.order_repository_Impl import OrderRepositoryImpl
from src.infrastructure.database.connection import get_db
from src.common_auth.common_auth.dependencies import get_current_user, get_raw_token

router = APIRouter()


def get_service(db=Depends(get_db)):
    return OrderService(OrderRepositoryImpl(db))

def serialize_order(order, service: OrderService,token: str):
    serialized_items = []
    for i in order.items:
        product = service.fetch_product(i.product_id, token)

        serialized_items.append({
            "product_id": i.product_id,
            "product_name": product.get("name"),
            "product_image": product.get("image"),
            "quantity": i.quantity,
            "price": i.price
        })

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "status": order.status.value if hasattr(order.status, "value") else order.status,
        "created_at": order.created_at,
        "items": serialized_items
    }


@router.post("/checkout", response_model=OrderResponse)
def place_order(
    service: OrderService = Depends(get_service),
    user=Depends(get_current_user),
    raw_token: str = Depends(get_raw_token)
):
    user_id = user["sub"]
    try:
        order = service.checkout(user_id, raw_token)
        return serialize_order(order,service,raw_token)
    except Exception as e:
        raise HTTPException(400, str(e))



@router.get("/", response_model=list[OrderResponse])
def list_orders(
    service: OrderService = Depends(get_service),
    user=Depends(get_current_user),
    raw_token: str = Depends(get_raw_token)
):
    user_id = user["sub"]
    orders = service.list_orders(user_id)

    return [serialize_order(o,service,raw_token) for o in orders]



@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    service: OrderService = Depends(get_service),
    user=Depends(get_current_user),
    raw_token: str = Depends(get_raw_token)
):
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    return serialize_order(order,service,raw_token)

