import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.infrastructure.database.connection import engine, Base
from src.api.routes import admin_route
from src.utils.logger import setup_logger
from src.utils.middleware.correlation import CorrelationIdMiddleware
from src.utils.middleware.exception import ExceptionMiddleware
from src.utils.middleware.rate_limiter import RateLimitMiddleware

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Admin Service started successfully")
    yield
    # Shutdown: Close connections
    logger.info("Shutting down User Service...")
    engine.dispose()

app = FastAPI(
    title="Admin Service",
    description="Microservice for Admin management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(ExceptionMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_route.router, prefix="/api/v1/admin")
# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "service": "user-service",
#         "status": "healthy",
#         "version": "1.0.0"
#     }