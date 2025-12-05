from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None