from fastapi import APIRouter, Depends, HTTPException, Query
from infrastructure.repositories.product_repository_Impl import ProductRepositoryImpl
from infrastructure.database.connection import get_db
from src.api.schemas.product_admin_schema import ProductApproveRequest
from common_auth.dependencies import get_current_user

router = APIRouter()

def get_repo(db = Depends(get_db)):
    return ProductRepositoryImpl(db)

@router.get("/low-stock")
def low_stock(
    threshold: int = Query(5, ge=0),
    user = Depends(get_current_user),
    repo: ProductRepositoryImpl = Depends(get_repo)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    products = repo.list_low_stock(threshold)
    return [
        {
            "product_id": p.id,
            "name": p.name,
            "stock": p.stock
        }
        for p in products
    ]

@router.post("/approve")
def approve_product(
    payload: ProductApproveRequest,
    user = Depends(get_current_user),
    repo: ProductRepositoryImpl = Depends(get_repo)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    product = repo.get(payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    product.is_active = payload.approve
    repo.save(product)

    return {
        "id": product.id,
        "name": product.name,
        "stock": product.stock,
        "is_active": product.is_active
    }

