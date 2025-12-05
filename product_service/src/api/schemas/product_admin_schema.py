from pydantic import BaseModel

class ProductApproveRequest(BaseModel):
    product_id: str
    approve: bool
