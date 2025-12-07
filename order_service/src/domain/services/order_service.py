import uuid
import requests
from datetime import datetime
from src.domain.interface.order_repository import OrderRepository
from src.infrastructure.database.order_model import Order, OrderItem, OrderStatus

CART_SERVICE_URL = "https://shop-easy-pro-api-cart.onrender.com/api/v1/Cart"
PRODUCT_SERVICE_URL = "https://shop-easy-pro-api-product.onrender.com/api/v1/Product"

class OrderService:

    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def fetch_product(self, product_id: str, token: str):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}", headers=headers)
            if res.status_code == 200:
                return res.json()
        except:
            pass


        return {
            "name": "Unknown Product",
            "image": None
        }

    def fetch_cart(self,  token: str):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{CART_SERVICE_URL}/", headers=headers)

        if response.status_code != 200:
            return []
        return response.json()["items"]



    def checkout(self, user_id: str,token: str):
        
        cart_items = self.fetch_cart(token)
        if not cart_items:
            raise Exception("Cart is empty")

        total = sum(i["price"] * i["quantity"] for i in cart_items)

        payment_success = True 
        if not payment_success:
            raise Exception("Payment failed")

        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            total_amount=total,
            status=OrderStatus.PAID
        )

        order_items = []
        for item in cart_items:
            order_items.append(
                OrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
            )

        saved_order = self.repo.create_order(order, order_items)
        headers = {"Authorization": f"Bearer {token}"}
        requests.delete(f"{CART_SERVICE_URL}/", headers=headers)

        return saved_order

    def list_orders(self, user_id: str):
        return self.repo.get_orders_by_user(user_id)

    def get_order(self, order_id: str):
        return self.repo.get_order(order_id)
