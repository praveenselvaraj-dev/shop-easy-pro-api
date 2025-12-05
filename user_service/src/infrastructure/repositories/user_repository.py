from sqlalchemy.orm import Session
from typing import Optional, List
from domain.interface.user_repository import IUserRepository
from domain.entities.user import User
from infrastructure.database.models import UserModel

class UserRepository(IUserRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            role=model.role if isinstance(model.role, str) else model.role.value,  # Handle both
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at
        )
    
    def create(self, username: str, email: str, password_hash: str, role: str) -> User:
        db_user = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_entity(user) for user in db_users]
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def get_password_hash(self, email: str) -> Optional[str]:
        db_user = self.db.query(UserModel).filter(UserModel.username == email).first()
        return db_user.password_hash if db_user else None