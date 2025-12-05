from abc import ABC, abstractmethod
from typing import Optional, List

from abc import ABC, abstractmethod
from typing import List, Optional

class ProductRepository(ABC):

    @abstractmethod
    def create(self, data): pass

    @abstractmethod
    def get_by_id(self, product_id: str): pass

    @abstractmethod
    def update(self, product_id: str, data: dict): pass

    @abstractmethod
    def delete(self, product_id: str) -> bool: pass

    @abstractmethod
    def list(
        self, 
        search: Optional[str], 
        category: Optional[str], 
        price_min: Optional[float],
        price_max: Optional[float],
        sort_by: Optional[str],
        sort_order: Optional[str],
        page: int,
        size: int
    ): pass
