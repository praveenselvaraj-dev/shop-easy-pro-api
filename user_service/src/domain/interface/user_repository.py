from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.user import User

class IUserRepository(ABC):
    
    @abstractmethod
    def create(self, username: str, email: str, password_hash: str, role: str) -> User:
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass
    
    @abstractmethod
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass