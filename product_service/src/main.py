import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.infrastructure.database.connection import engine, Base
from src.api.routes import product_routes,product_admin_route
from src.utils.logger import setup_logger
from fastapi.staticfiles import StaticFiles
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Product Service started successfully")
    yield
    logger.info("Shutting down User Service...")
    engine.dispose()

app = FastAPI(
    title="Product Service",
    description="Microservice for Product management",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_routes.router, prefix="/api/v1/Product", tags=["Products"])
app.include_router(product_admin_route.router, prefix="/api/v1/admin/Product", tags=["Product admin"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
