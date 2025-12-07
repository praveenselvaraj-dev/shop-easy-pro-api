from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str 
    
    
    JWT_SECRET_KEY: str = "supersecret123"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis (for caching)
    # REDIS_URL: str = "redis://localhost:6379"
    
   
    SERVICE_NAME: str = "product-service"
    SERVICE_PORT: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()