import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

from src.infrastructure.database.connection import engine, Base
from src.api.routes import cart_route
from src.utils.logger import setup_logger
from src.utils.exceptions import NotEnoughStock, ProductNotFound, CartItemNotFound

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Create database tables
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Cart Service started successfully")
    yield
    # Shutdown: Close connections
    logger.info("Shutting down User Service...")
    engine.dispose()

app = FastAPI(
    title="Cart Service",
    description="Microservice for Cart management",
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

@app.exception_handler(NotEnoughStock)
async def not_enough_stock_handler(request: Request, exc: NotEnoughStock):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(ProductNotFound)
async def product_not_found_handler(request: Request, exc: ProductNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(CartItemNotFound)
async def cart_item_not_found_handler(request: Request, exc: CartItemNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

# Include Routers
app.include_router(cart_route.router, prefix="/api/v1/Cart", tags=["Cart"])

# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "service": "user-service",
#         "status": "healthy",
#         "version": "1.0.0"
#     }