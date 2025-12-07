from fastapi import APIRouter, Depends, Query, HTTPException
from common_auth.dependencies import  admin_required, get_current_user, get_raw_token
from src.api.dependencies import get_admin_service
from src.api.schemas.admin_schema import SalesSummary, LowStockItem, PagedOrders, OrderResponse, ApproveRequest, AuditLogResponse

router = APIRouter(tags=["admin"])

@router.get("/sales", response_model=SalesSummary)
def sales_summary(from_date: str | None = Query(None), to_date: str | None = Query(None),
                  service = Depends(get_admin_service), user = Depends(admin_required), token: str = Depends(get_raw_token)):
    return service.get_sales_summary(from_date, to_date, token)

@router.get("/low-stock", response_model=list[LowStockItem])
def low_stock(threshold: int = Query(5), service = Depends(get_admin_service), user = Depends(admin_required),token: str = Depends(get_raw_token)):
    return service.get_low_stock(threshold, token)

# @router.get("/orders", response_model=PagedOrders)
# def list_orders(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=200),
#                 service = Depends(get_admin_service), user = Depends(admin_required),raw_token: str = Depends(get_raw_token)):
#     return service.get_orders(page, size, raw_token)

# @router.get("/orders/{order_id}", response_model=OrderResponse)
# def get_order(
#     order_id: str,
#     service = Depends(get_admin_service),
#     user = Depends(admin_required),
#     raw_token: str = Depends(get_raw_token)
#     ):
#         order = service.get_order(order_id, raw_token)
#         if not order:
#             raise HTTPException(status_code=404, detail="Order not found")
#         return order


# @router.post("/approve")
# def approve(req: ApproveRequest, service = Depends(get_admin_service), user = Depends(admin_required), token: str = Depends(get_raw_token) ):
#     res = service.approve(req.entity, req.entity_id, req.approve, user["sub"], token)
#     if not res:
#         raise HTTPException(status_code=404, detail="Entity not found")
#     return res
