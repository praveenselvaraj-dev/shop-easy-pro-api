from fastapi import APIRouter, Depends, Query, HTTPException
from infrastructure.database.connection import get_db
from infrastructure.repositories.order_repository_Impl import OrderRepositoryImpl
from common_auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter()

def get_repo(db=Depends(get_db)):
    return OrderRepositoryImpl(db)

@router.get("/sales")
def admin_sales(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    user=Depends(get_current_user),
    repo: OrderRepositoryImpl = Depends(get_repo)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    try:
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Expected ISO format YYYY-MM-DD"
        )

    return repo.sales_summary(from_dt, to_dt)
