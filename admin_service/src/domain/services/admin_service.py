from datetime import datetime
from typing import Optional
from src.infrastructure.repositories.admin_repository_Impl import AdminRepositoryImpl

class AdminService:
    def __init__(self, repo: AdminRepositoryImpl):
        self.repo = repo

    def get_sales_summary(self, from_date: Optional[str], to_date: Optional[str], token):
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None
        return self.repo.fetch_sales_summary(from_dt, to_dt,token)

    def get_low_stock(self, threshold, token):
        return self.repo.fetch_low_stock(threshold, token)


    def get_orders(self, page, size, token):
        return self.repo.fetch_orders(page, size, token)


    def get_order(self, order_id: str, token: str):
        return self.repo.fetch_order_details(order_id, token)


    def approve(self, entity: str, entity_id: str, approve: bool, actor: str, token: str):
        return self.repo.approve_entity(entity, entity_id, approve, actor, token)

