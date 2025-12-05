import os, requests
from sqlalchemy.orm import Session
from src.infrastructure.database.Audit_log import AuditLog
from src.utils.utils import safe_json

USER_SERVICE = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8000/api/v1/User")
PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:8001/api/v1/admin/Product")
ORDER_SERVICE = os.getenv("ORDER_SERVICE_URL", "http://127.0.0.1:8003/api/v1/admin/Order")

TIMEOUT = 5 

class AdminRepositoryImpl:
    def __init__(self, db: Session):
        self.db = db

    def _headers(self, token):
        return {"Authorization": f"Bearer {token}"} if token else {}

    
    def fetch_sales_summary(self, from_dt, to_dt, token=None):
        params = {}
        if from_dt: 
            params["from_date"] = from_dt.isoformat()
        if to_dt: 
            params["to_date"] = to_dt.isoformat()

        try:
            r = requests.get(
            f"{ORDER_SERVICE}/sales",
            params=params,
            headers=self._headers(token),
            timeout=TIMEOUT
         )
        except requests.exceptions.RequestException:
            return {
            "total_sales": 0.0, 
            "total_orders": 0,
            "from_date": from_dt.strftime("%d-%m-%Y") if from_dt else None,
            "to_date": to_dt.strftime("%d-%m-%Y") if to_dt else None
        }

        result = r.json() if r.status_code == 200 else {"total_sales": 0.0, "total_orders": 0}

        
        result["from_date"] = from_dt.strftime("%d-%m-%Y") if from_dt else None
        result["to_date"] = to_dt.strftime("%d-%m-%Y") if to_dt else None

        return result

    
    def fetch_low_stock(self, threshold=5, token=None):
        try:
            r = requests.get(
                f"{PRODUCT_SERVICE}/low-stock",
                params={"threshold": threshold},
                headers=self._headers(token),
                timeout=TIMEOUT
            )
        except requests.exceptions.RequestException:
            return []

        return r.json() if r.status_code == 200 else []

    
    def fetch_orders(self, page: int, size: int, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        r = requests.get(
            f"{ORDER_SERVICE}/",
            params={"page": page, "size": size},
            headers=headers
        )

        data = safe_json(r)

       
        if isinstance(data, list):
            return {
                "total": len(data),
                "page": page,
                "size": size,
                "items": data
            }

       
        if isinstance(data, dict):
            return {
                "total": 1,
                "page": page,
                "size": size,
                "items": [data]
            }

        
        return {
            "total": 0,
            "page": page,
            "size": size,
            "items": []
        }




  
    def fetch_order_details(self, order_id: str, token=None):
        r = requests.get(
            f"{ORDER_SERVICE}/{order_id}",
            headers=self._headers(token),
            timeout=TIMEOUT
        )

        if r.status_code == 200:
            return r.json()

        return None


    
    def approve_entity(self, entity: str, entity_id: str, approve: bool, actor: str, token=None):
        if entity == "product":
            try:
                r = requests.post(
                    f"{PRODUCT_SERVICE}/approve",
                    json={"product_id": entity_id, "approve": approve},
                    headers=self._headers(token),
                    timeout=TIMEOUT
                )
            except requests.exceptions.RequestException:
                return None
            
            if r.status_code not in (200, 201):
                return None

           
            log = AuditLog(
                actor=actor,
                action="approve_product",
                details=f"product_id={entity_id}, approve={approve}"
            )
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)

            return r.json()

        
        return None
