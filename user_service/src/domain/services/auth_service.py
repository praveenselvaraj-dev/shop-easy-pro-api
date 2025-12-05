from typing import Optional
from domain.interface.user_repository import IUserRepository
from config.security import verify_password, hash_password, create_access_token
from utils.exceptions import InvalidCredentialsError, UserAlreadyExistsError

class AuthService:
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repo = user_repository
    
    def register(self, username: str, email: str, password: str, role: str) -> dict:

        if self.user_repo.get_by_email(email):
            raise UserAlreadyExistsError("Email already registered")
        
        if self.user_repo.get_by_username(username):
            raise UserAlreadyExistsError("Username already taken")
        
        try:
            password_hash = hash_password(password)
            print(f"Password hashed successfully. Hash length: {len(password_hash)}")
        except Exception as e:
            print(f"ERROR during hashing: {e}")
            raise
        user = self.user_repo.create(username, email, password_hash, role)
        
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        
        return {
            "data": user,
            "status": "Registeration Success",
            "message": "bearer"
        }
    
    def login(self, username: str, password: str) -> dict:
        user = self.user_repo.get_by_username(username)
        
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        
        password_hash = self.user_repo.get_password_hash(username)
        
        if not verify_password(password, password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        
        if not user.is_active:
            raise InvalidCredentialsError("Account is inactive")
        
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }