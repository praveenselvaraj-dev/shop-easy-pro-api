import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2] 
sys.path.append(str(ROOT_DIR))
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

from src.infrastructure.database.connection import engine, Base
from src.api.routes import cart_route
from src.utils.logger import setup_logger
from src.utils.exceptions import NotEnoughStockError, ProductNotFoundError, CartItemNotFoundError
from src.utils.middleware.correlation import CorrelationIdMiddleware
from src.utils.middleware.exception import ExceptionMiddleware
from src.utils.middleware.rate_limiter import RateLimitMiddleware

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Cart Service started successfully")
    yield
    logger.info("Shutting down Cart Service...")
    engine.dispose()

app = FastAPI(
    title="Cart Service",
    description="Microservice for Cart management",
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

@app.exception_handler(NotEnoughStockError)
async def not_enough_stock_handler(request: Request, exc: NotEnoughStockError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(ProductNotFoundError)
async def product_not_found_handler(request: Request, exc: ProductNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(CartItemNotFoundError)
async def cart_item_not_found_handler(request: Request, exc: CartItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

app.include_router(cart_route.router, prefix="/api/v1/Cart", tags=["Cart"])

# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "service": "user-service",
#         "status": "healthy",
#         "version": "1.0.0"
#     }