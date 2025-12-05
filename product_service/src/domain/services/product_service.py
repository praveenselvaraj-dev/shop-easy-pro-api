import os
from fastapi import UploadFile
class ProductService:

    def __init__(self, repo):
        self.repo = repo

    def create(self, data):
        return self.repo.create(data)

    def get(self, product_id):
        return self.repo.get_by_id(product_id)


    def update(self, product_id: str, data: dict, image: UploadFile | None = None):
        if image:
            data["image"] = image  
        return self.repo.update(product_id, data)

    def delete(self, product_id):
        return self.repo.delete(product_id)

    def list(self, search, category, price_min, price_max, sort_by, sort_order, page, size):
        total, products = self.repo.list(
            search, category, price_min, price_max, sort_by, sort_order, page, size
        )
        return total, products
