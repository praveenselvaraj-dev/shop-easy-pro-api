from abc import ABC, abstractmethod


class OrderRepository(ABC):

    @abstractmethod
    def create_order(self, order, items):
        pass

    @abstractmethod
    def get_orders_by_user(self, user_id: str):
        pass

    @abstractmethod
    def get_order(self, order_id: str):
        pass
