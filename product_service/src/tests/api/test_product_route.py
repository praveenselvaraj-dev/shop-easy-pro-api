# test_product_route.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from src.main import app
from src.api.routes.product_routes import get_service
from common_auth.dependencies import get_current_user
from datetime import datetime

client = TestClient(app)

def mock_admin_user():
    return {"user_id": "admin-123", "role": "admin"}

def mock_non_admin_user():
    return {"user_id": "user-123", "role": "user"}

def create_product_dict(product_id="prod-1", name="Test Product", price=100.0, stock=10):
    """Create a product dictionary that matches ProductResponse schema"""
    return {
        "id": product_id,
        "name": name,
        "description": "Test Description",
        "price": price,
        "stock": stock,
        "category": "Electronics",
        "image": "http://example.com/image.jpg",
        "approved": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

class MockProduct:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "prod-1")
        self.name = kwargs.get("name", "Test Product")
        self.description = kwargs.get("description", "Test Description")
        self.price = kwargs.get("price", 100.0)
        self.stock = kwargs.get("stock", 10)
        self.category = kwargs.get("category", "Electronics")
        self.image = kwargs.get("image", "http://example.com/image.jpg")
        self.approved = kwargs.get("approved", True)
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())
    
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "image": self.image,
            "approved": self.approved,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def model_dump(self):
        return self.dict()
    
    def __iter__(self):
        return iter(self.dict().items())

@pytest.fixture
def mock_service():
    service = Mock()
    return service

@pytest.fixture(autouse=True)
def setup_dependencies(mock_service):
    """Setup dependency overrides for all tests"""
    app.dependency_overrides[get_current_user] = mock_admin_user
    app.dependency_overrides[get_service] = lambda: mock_service
    yield
    app.dependency_overrides.clear()

def test_create_product_success(mock_service):
    mock_product = MockProduct(id="uuid-test-123", name="Test Product")
    mock_service.create.return_value = mock_product
    
    response = client.post(
        "/api/v1/Product/",
        data={
            "name": "Test Product",
            "description": "Description",
            "price": 100.0,
            "stock": 10,
            "category": "Electronics"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "uuid-test-123"
    assert data["name"] == "Test Product"
    mock_service.create.assert_called_once()

def test_create_product_non_admin(mock_service):
    app.dependency_overrides[get_current_user] = mock_non_admin_user
    
    response = client.post(
        "/api/v1/Product/",
        data={
            "name": "Test Product",
            "price": 100.0,
            "stock": 10
        }
    )
    
    assert response.status_code == 403
    assert "Admin can only create" in response.json()["detail"]

def test_reserve_stock_success(mock_service):
    mock_product = MockProduct(stock=10)
    updated_product = MockProduct(stock=8)
    
    mock_service.get.return_value = mock_product
    mock_service.update.return_value = updated_product
    
    response = client.post("/api/v1/Product/prod-1/reserve?quantity=2")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["stock"] == 8
    mock_service.update.assert_called_once_with("prod-1", {"stock": 8})

def test_reserve_stock_insufficient(mock_service):
    mock_product = MockProduct(stock=5)
    mock_service.get.return_value = mock_product
    
    response = client.post("/api/v1/Product/prod-1/reserve?quantity=10")
    
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_reserve_stock_not_found(mock_service):
    mock_service.get.return_value = None
    
    response = client.post("/api/v1/Product/nonexistent/reserve?quantity=2")
    
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]

def test_restore_stock_success(mock_service):
    mock_product = MockProduct(stock=8)
    updated_product = MockProduct(stock=10)
    
    mock_service.get.return_value = mock_product
    mock_service.update.return_value = updated_product
    
    response = client.post("/api/v1/Product/prod-1/restore?quantity=2")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["stock"] == 10

def test_get_product_success(mock_service):
    mock_product = MockProduct()
    mock_service.get.return_value = mock_product
    
    response = client.get("/api/v1/Product/prod-1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "prod-1"
    assert data["name"] == "Test Product"

def test_get_product_not_found(mock_service):
    mock_service.get.return_value = None
    
    response = client.get("/api/v1/Product/nonexistent")
    
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]

def test_list_products(mock_service):
    mock_product = MockProduct()
    mock_service.list.return_value = (1, [mock_product])
    
    response = client.get("/api/v1/Product/?page=1&size=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert len(data["products"]) == 1
    assert data["products"][0]["name"] == "Test Product"

def test_update_product_success(mock_service):
    updated_product = MockProduct(name="Updated Product", price=150.0)
    mock_service.update.return_value = updated_product
    
    response = client.put(
        "/api/v1/Product/prod-1",
        data={"name": "Updated Product", "price": "150.0"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["price"] == 150.0

def test_update_product_non_admin(mock_service):
    app.dependency_overrides[get_current_user] = mock_non_admin_user
    
    response = client.put(
        "/api/v1/Product/prod-1",
        data={"name": "Updated"}
    )
    
    assert response.status_code == 403

def test_update_product_nothing_to_update(mock_service):
    response = client.put("/api/v1/Product/prod-1", data={})
    
    assert response.status_code == 400
    assert "Nothing to update" in response.json()["detail"]

def test_update_product_not_found(mock_service):
    mock_service.update.return_value = None
    
    response = client.put(
        "/api/v1/Product/nonexistent",
        data={"name": "Updated"}
    )
    
    assert response.status_code == 404

def test_delete_product_success(mock_service):
    mock_service.delete.return_value = True
    
    response = client.delete("/api/v1/Product/prod-1")
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_delete_product_not_found(mock_service):
    mock_service.delete.return_value = False
    
    response = client.delete("/api/v1/Product/nonexistent")
    
    assert response.status_code == 404

def test_delete_product_non_admin(mock_service):
    app.dependency_overrides[get_current_user] = mock_non_admin_user
    mock_service.delete.return_value = True
    
    response = client.delete("/api/v1/Product/prod-1")
    
    assert response.status_code == 403