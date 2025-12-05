from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from infrastructure.database.product_model import ProductTable
from domain.interface.product_repository import ProductRepository
import shutil
import uuid
from pathlib import Path
class ProductRepositoryImpl(ProductRepository):

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict):
        image = data.pop("image", None)
        image_url = None

        if image:
                ext = Path(image.filename).suffix
                filename = f"{uuid.uuid4()}{ext}"
                filepath = Path("uploads/products") / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with filepath.open("wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                image_url = f"/uploads/products/{filename}"


                product = ProductTable(**data, image=image_url)
                self.db.add(product)
                self.db.commit()
                self.db.refresh(product)
                return product



    def get_by_id(self, product_id: str):
        return self.db.query(ProductTable).filter(ProductTable.id == product_id).first()


    def update(self, product_id: str, data: dict):
        product = self.get_by_id(product_id)
        if not product:
            return None

        image = data.pop("image", None)

  
        if image:
            ext = Path(image.filename).suffix
            filename = f"{uuid.uuid4()}{ext}"
            filepath = Path("uploads/products") / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with filepath.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
                product.image = f"/uploads/products/{filename}"

        for key, value in data.items():
            if value is not None:
                setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)
        return product



    def delete(self, product_id: str):
        product = self.get_by_id(product_id)
        if not product:
            return False

        self.db.delete(product)
        self.db.commit()
        return True

    def list(
        self, 
        search,
        category,
        price_min,
        price_max,
        sort_by,
        sort_order,
        page,
        size
    ):
        query = self.db.query(ProductTable)

        
        if search:
            query = query.filter(ProductTable.name.ilike(f"%{search}%"))

        
        if category:
            query = query.filter(ProductTable.category == category)

        
        if price_min is not None:
            query = query.filter(ProductTable.price >= price_min)

        if price_max is not None:
            query = query.filter(ProductTable.price <= price_max)

        
        if sort_by:
            sort_field = getattr(ProductTable, sort_by, None)
            if sort_field:
                query = query.order_by(
                    asc(sort_field) if sort_order == "asc" else desc(sort_field)
                )

       
        total = query.count()
        products = query.offset((page - 1) * size).limit(size).all()

        return total, products
    
    def list_low_stock(self, threshold: int):
        return self.db.query(ProductTable).filter(ProductTable.stock <= threshold).all()

    def save(self, product):
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get(self, product_id: str):
        return self.db.query(ProductTable).filter(ProductTable.id == product_id).first()