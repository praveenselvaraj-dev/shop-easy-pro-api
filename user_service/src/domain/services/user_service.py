from typing import List, Optional
from src.domain.interface.user_repository import IUserRepository
from src.domain.entities.user import User
from src.utils.exceptions import UserNotFoundError

class UserService:
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repo = user_repository
    
    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_email(email)
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repo.get_all(skip, limit)
    
    def update_user(self, user_id: int, **kwargs) -> User:
        user = self.user_repo.update(user_id, **kwargs)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user
    
    def delete_user(self, user_id: int) -> bool:
        success = self.user_repo.delete(user_id)
        if not success:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return True