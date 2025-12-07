from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import get_settings
from src.utils.logger import setup_logger
logger = setup_logger(__name__)

settings = get_settings()
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, 
    echo=False
)
logger.info(f"Connected DB URL: {settings.DATABASE_URL}")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()