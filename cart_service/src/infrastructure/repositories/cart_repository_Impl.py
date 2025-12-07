from sqlalchemy.orm import Session
from src.infrastructure.database.cart_model import CartItem
from src.domain.interface.cart_repository import CartRepository

class CartRepositoryImpl(CartRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_cart(self, user_id: str):
        return self.db.query(CartItem).filter(CartItem.user_id == user_id).all()

    def get_item(self, user_id: str, product_id: str):
        return self.db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id
        ).first()
    
    def get_item_by_id(self, product_id: str):
        return self.db.query(CartItem).get(product_id)


    def add_item(self, user_id: str, product_id: str, quantity: int, price: float):
        item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            price=price
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id: str, quantity: int):
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return None
        item.quantity = quantity
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: str):
        item = self.db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            return None
        self.db.delete(item)
        self.db.commit()
        return True

    def clear_cart(self, user_id: str):
        self.db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        self.db.commit()
        return True
