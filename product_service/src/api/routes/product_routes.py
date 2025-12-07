from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from typing import Optional, List
from domain.services.product_service import ProductService
from infrastructure.repositories.product_repository_Impl import ProductRepositoryImpl
from infrastructure.database.connection import get_db
from common_auth.dependencies import get_current_user
from src.utils.exceptions import (
    ProductNotFoundError,
    UnauthorizedError,
    InsufficientStockError
)
from api.schemas.product_schema import ProductCreateRequest, ProductUpdateRequest, ProductResponse, PaginatedProductResponse

router = APIRouter()

# Dependency to get ProductService
def get_service(db=Depends(get_db)):
    return ProductService(ProductRepositoryImpl(db))


@router.post("/", response_model=ProductResponse)
def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user),
    service: ProductService = Depends(get_service)
):
    if user.get("role") != "admin":
        raise UnauthorizedError("Admin can only create a product")

    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category,
        "image": image,
    }

    return service.create(product_data)


@router.post("/{product_id}/reserve")
def reserve_stock(
    product_id: str,
    quantity: int = Query(..., ge=1),
    service: ProductService = Depends(get_service)
):
    product = service.get(product_id)
    if not product:
        raise ProductNotFoundError(f"Product with ID {product_id} not found")

    if product.stock < quantity:
        raise InsufficientStockError(f"Insufficient stock for product {product_id}")

    updated = service.update(product_id, {"stock": product.stock - quantity})
    return {"status": "success", "stock": updated.stock}


@router.post("/{product_id}/restore")
def restore_stock(
    product_id: str,
    quantity: int = Query(..., ge=1),
    service: ProductService = Depends(get_service)
):
    product = service.get(product_id)
    if not product:
        raise ProductNotFoundError(f"Product with ID {product_id} not found")

    updated = service.update(product_id, {"stock": product.stock + quantity})
    return {"status": "success", "stock": updated.stock}


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    user: dict = Depends(get_current_user),
    service: ProductService = Depends(get_service)
):
    product = service.get(product_id)
    if not product:
        raise ProductNotFoundError(f"Product with ID {product_id} not found")
    return product


@router.get("/", response_model=PaginatedProductResponse)
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    user: dict = Depends(get_current_user),
    service: ProductService = Depends(get_service)
):
    total, products = service.list(
        search, category, price_min, price_max, sort_by, sort_order, page, size
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "products": products
    }


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    image: Optional[UploadFile] = None,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    category: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
    service: ProductService = Depends(get_service)
):
    if user.get("role") != "admin":
        raise UnauthorizedError("Admin can only update a product")

    update_data = {k: v for k, v in {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category
    }.items() if v is not None}

    if not update_data and not image:
        raise ValueError("Nothing to update")  # will be handled by middleware

    product = service.update(product_id, update_data, image)
    if not product:
        raise ProductNotFoundError(f"Product with ID {product_id} not found")

    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    user: dict = Depends(get_current_user),
    service: ProductService = Depends(get_service)
):
    if user.get("role") != "admin":
        raise UnauthorizedError("Admin can only delete a product")

    success = service.delete(product_id)
    if not success:
        raise ProductNotFoundError(f"Product with ID {product_id} not found")

    return {"message": "Product deleted successfully"}
