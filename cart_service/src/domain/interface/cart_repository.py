from abc import ABC, abstractmethod

class CartRepository(ABC):

    @abstractmethod
    def get_cart(self, user_id: str):
        pass

    @abstractmethod
    def get_item(self, user_id: str, product_id: str):
        pass

    @abstractmethod
    def get_item_by_id(self, product_id: str):
        pass

    @abstractmethod
    def add_item(self, user_id: str, product_id: str, quantity: int, price: float):
        pass

    @abstractmethod
    def update_item(self, user_id: str,product_id: str, quantity: int):
        pass

    @abstractmethod
    def delete_item(self, product_id: str):
        pass

    @abstractmethod
    def clear_cart(self, user_id: str):
        pass
