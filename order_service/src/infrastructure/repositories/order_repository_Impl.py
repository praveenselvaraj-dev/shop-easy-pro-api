import uuid
from sqlalchemy.orm import Session
from src.infrastructure.database.order_model import Order, OrderItem
from sqlalchemy import func

class OrderRepositoryImpl:

    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order, items):
        self.db.add(order)

        for i in items:
            self.db.add(i)


        self.db.commit()
        self.db.refresh(order)   
        return order       


    def get_orders_by_user(self, user_id: str):
        return self.db.query(Order).filter(Order.user_id == user_id).all()

    def get_order(self, order_id: str):
        return self.db.query(Order).filter(Order.id == order_id).first()


    def sales_summary(self, from_dt=None, to_dt=None):
        q = self.db.query(
        func.sum(Order.total_amount).label("total_sales"),
        func.count(Order.id).label("total_orders")
        )

        if from_dt:
            q = q.filter(Order.created_at >= from_dt)
        if to_dt:
            q = q.filter(Order.created_at <= to_dt)

        res = q.one()
        return {
        "total_sales": float(res.total_sales or 0),
        "total_orders": int(res.total_orders or 0)
        }
