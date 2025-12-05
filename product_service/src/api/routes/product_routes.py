from fastapi import APIRouter, Depends, HTTPException,UploadFile, File, Form, Query
from api.schemas.product_schema import (
    ProductCreateRequest, ProductUpdateRequest,
    ProductResponse, PaginatedProductResponse
)
from typing import Optional
from domain.services.product_service import ProductService
from infrastructure.repositories.product_repository_Impl import ProductRepositoryImpl
from infrastructure.database.connection import get_db
from common_auth.dependencies import get_current_user

from infrastructure.cache.redis_client import cache_get, cache_set, cache_delete
router = APIRouter()

def get_service(db=Depends(get_db)):
    return ProductService(ProductRepositoryImpl(db))


@router.post("/", response_model=ProductResponse)
def create_product(
    name: str = Form(...),
    description: str | None = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category: str | None = Form(None),
    image: UploadFile | None = File(None),
    user: dict = Depends(get_current_user),
    service: "ProductService" = Depends(get_service)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin can only create a product...")

    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category,
        "image": image,
    }
    cache_delete("products:all")

    return service.create(product_data)

@router.post("/{product_id}/reserve")
def reserve_stock(
    product_id: str,
    quantity: int = Query(..., ge=1),
    service: ProductService = Depends(get_service)
):
    product = service.get(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    if product.stock < quantity:
        raise HTTPException(400, "Insufficient stock")

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
        raise HTTPException(404, "Product not found")

    updated = service.update(product_id, {"stock": product.stock + quantity})
    return {"status": "success", "stock": updated.stock}

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, user: dict = Depends(get_current_user),service: ProductService = Depends(get_service)):
    
    cache_key = f"product:{product_id}"

    cached = cache_get(cache_key)
    if cached:
        return cached
    
    product = service.get(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product



@router.get("/", response_model=PaginatedProductResponse)
def list_products(
    search: str = Query(None),
    category: str = Query(None),
    price_min: float = Query(None),
    price_max: float = Query(None),
    sort_by: str = Query(None, example="price"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    user: dict = Depends(get_current_user),
    service: ProductService = Depends(get_service)
):
    

    cache_key = f"products:all:{search}:{category}:{price_min}:{price_max}:{sort_by}:{sort_order}:{page}:{size}"

    cached = cache_get(cache_key)
    if cached:
        return cached
    

    total, products = service.list(
        search, category, price_min, price_max, sort_by, sort_order, page, size
    )
    
    response = {
        "total": total,
        "page": page,
        "size": size,
        "products": products
    }
    cache_set(cache_key, response, ttl=120)

    return response


@router.put("/{product_id}")
def update_product(
        product_id: str,
        image: Optional[UploadFile] = None,
        name: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        price: Optional[float] = Form(None),
        stock: Optional[int] = Form(None),
        category: Optional[str] = Form(None),
        user: dict = Depends(get_current_user),
        service: ProductService = Depends(get_service),
    ):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin can only update a product")

    update_data = {k: v for k, v in {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category
    }.items() if v is not None}

    if not update_data and not image:
        raise HTTPException(status_code=400, detail="Nothing to update")

    product = service.update(product_id, update_data, image)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cache_delete("products:all")
    cache_delete(f"product:{product_id}")


    return product

@router.delete("/{product_id}")
def delete_product(product_id: str,user: dict = Depends(get_current_user) ,service: ProductService = Depends(get_service)):
    success = service.delete(product_id)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin can only Delete a Product...")
    if not success:
        raise HTTPException(404, "Product not found")
    

    cache_delete("products:all")
    cache_delete(f"product:{product_id}")

    
    return {"message": "Product deleted successfully"}
