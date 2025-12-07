import requests
from src.domain.interface.cart_repository import CartRepository
from src.utils.exceptions import NotEnoughStockError, ProductNotFoundError, CartItemNotFoundError
from fastapi import HTTPException

PRODUCT_SERVICE_URL = "http://127.0.0.1:8001/api/v1/Product"


class CartService:

    def __init__(self, repo: CartRepository):
        self.repo = repo

    def fetch_product_details(self, product_id: str, token: str="TEST_TOKEN"):
        if token.startswith("Bearer "):
            headers = {"Authorization": token}
        else:
            headers = {"Authorization": f"Bearer {token}"}

        url = f"{PRODUCT_SERVICE_URL}/{product_id}"

        res = requests.get(url, headers=headers)

        if res.status_code == 404:
            raise ProductNotFoundError("Product not found")

        if res.status_code == 403:
            raise HTTPException(403, "Unauthorized to access product service")

        if res.status_code != 200:
            raise HTTPException(500, "Failed to fetch product details")

        return res.json()


    def fetch_product_price(self, product_id: str, token: str="TEST_TOKEN"):
        data = self.fetch_product_details(product_id, token)
        if not data:
            return None

        return {
            "price": data["price"],
            "name": data["name"],
            "image": data["image"]
        }

    def reserve_stock(self, product_id: str, qty: int, token: str="TEST_TOKEN"):
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{PRODUCT_SERVICE_URL}/{product_id}/reserve?quantity={qty}"
        r = requests.post(url, headers=headers)
        return r.status_code == 200

    def restore_stock(self, product_id: str, qty: int, token: str="TEST_TOKEN"):
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{PRODUCT_SERVICE_URL}/{product_id}/restore?quantity={qty}"
        requests.post(url, headers=headers)

    def get_cart(self, user_id: str):
        return self.repo.get_cart(user_id)

    def add_to_cart(self, user_id: str, product_id: str, quantity: int, token: str="TEST_TOKEN"):
        product = self.fetch_product_price(product_id, token)

        if not product:
            raise ProductNotFoundError("Product not found")

        price = product["price"]

        existing = self.repo.get_item(user_id, product_id)

        if existing:
            diff = quantity
            if not self.reserve_stock(product_id, diff, token):
                raise NotEnoughStockError("Not enough stock")

            return self.repo.update_item(existing.id, existing.quantity + quantity)

        
        if not self.reserve_stock(product_id, quantity, token):
            raise NotEnoughStockError("Not enough stock")

        return self.repo.add_item(user_id, product_id, quantity, price)

    def update_quantity(self, item_id: str, quantity: int, user_id: str, token: str="TEST_TOKEN"):
        item = self.repo.get_item_by_id(item_id)

        if not item or item.user_id != user_id:
            raise CartItemNotFoundError("Item not found")

        diff = quantity - item.quantity

        if diff > 0:
            if not self.reserve_stock(item.product_id, diff, token):
                raise NotEnoughStockError("Not enough stock")
        elif diff < 0:
            self.restore_stock(item.product_id, abs(diff), token)

        return self.repo.update_item(item_id, quantity)

    def delete_item(self, item_id: str, user_id: str, token: str="TEST_TOKEN"):
        item = self.repo.get_item_by_id(item_id)
        if not item or item.user_id != user_id:
            return None

        self.restore_stock(item.product_id, item.quantity, token)
        return self.repo.delete_item(item_id)

    def clear_cart(self, user_id: str, token: str="TEST_TOKEN"):
        items = self.repo.get_cart(user_id)
        for item in items:
            self.restore_stock(item.product_id, item.quantity, token)
        return self.repo.clear_cart(user_id)
