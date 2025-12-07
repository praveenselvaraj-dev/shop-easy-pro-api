from fastapi import APIRouter, Depends
from fastapi import Query
from infrastructure.database.connection import get_db
from infrastructure.repositories.order_repository_Impl import OrderRepositoryImpl
from common_auth.dependencies import get_current_user
from datetime import datetime
from src.utils.exceptions import ForbiddenError, InvalidRequestError

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
    # if user.get("role") != "admin":
    #     raise ForbiddenError("Admin only")

    try:
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None
    except ValueError:
        raise InvalidRequestError(
            "Invalid date format. Expected ISO format YYYY-MM-DD"
        )

    return repo.sales_summary(from_dt, to_dt)
