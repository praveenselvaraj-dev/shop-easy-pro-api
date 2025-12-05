from abc import ABC, abstractmethod
from datetime import datetime

class AdminRepository(ABC):
    @abstractmethod
    def fetch_sales_summary(self, from_dt: datetime | None, to_dt: datetime | None, token=None): pass
    @abstractmethod
    def fetch_low_stock(self, threshold: int, token: str): pass
    @abstractmethod
    def fetch_orders(self, page: int, size: int): pass
    @abstractmethod
    def fetch_order_details(self, order_id: str): pass
    @abstractmethod
    def approve_entity(self, entity: str, entity_id: str, approve: bool, actor: str): pass
