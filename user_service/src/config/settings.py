from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
 
    DATABASE_URL: str = "postgresql+psycopg2://postgres:admin123@localhost:5432/postgres"
    
    JWT_SECRET_KEY: str = "supersecret123"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()