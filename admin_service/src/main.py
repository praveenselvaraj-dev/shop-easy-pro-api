import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.infrastructure.database.connection import engine, Base
from src.api.routes import admin_route
from src.utils.logger import setup_logger

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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(admin_route.router, prefix="/api/v1/admin")
# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "service": "user-service",
#         "status": "healthy",
#         "version": "1.0.0"
#     }