import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2] 
sys.path.append(str(ROOT_DIR))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.infrastructure.database.connection import engine, Base
from src.api.routes import order_routes,order_admin_route
from src.utils.logger import setup_logger
from src.utils.middleware.correlation import CorrelationIdMiddleware
from src.utils.middleware.exception import ExceptionMiddleware
from src.utils.middleware.rate_limiter import RateLimitMiddleware
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    # Base.metadata.create_all(bind=engine)
    logger.info("Order Service started successfully")
    yield
    logger.info("Shutting down Order Service...")
    engine.dispose()



app = FastAPI(
    title="Order Service",
    description="Microservice for Order management",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shop-easy-pro.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(order_routes.router, prefix="/api/v1/Order", tags=["Order"])
app.include_router(order_admin_route.router, prefix= "/api/v1/admin/Order", tags=["Order admin"])

# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "service": "user-service",
#         "status": "healthy",
#         "version": "1.0.0"
#     }