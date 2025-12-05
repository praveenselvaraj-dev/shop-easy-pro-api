from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    role: str = Field(..., min_length=3, max_length=50)
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) > 72:
            raise ValueError('Password cannot be longer than 72 characters')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "role": "user/admin"
            }
        }

class LoginRequest(BaseModel):
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john",
                "password": "SecurePass123"
            }
        }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RegisterResponse(BaseModel):
    status: str
    message: str
    data: dict