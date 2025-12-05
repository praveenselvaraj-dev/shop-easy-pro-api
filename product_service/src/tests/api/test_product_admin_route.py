# test_product_admin_route.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from src.main import app
from src.api.routes.product_admin_route import get_repo
from common_auth.dependencies import get_current_user

client = TestClient(app)

def mock_admin_user():
    return {"user_id": "admin-123", "role": "admin"}

def mock_non_admin_user():
    return {"user_id": "user-123", "role": "user"}

@pytest.fixture
def mock_repo():
    repo = Mock()
    return repo

@pytest.fixture(autouse=True)
def setup_dependencies(mock_repo):
    app.dependency_overrides[get_current_user] = mock_admin_user
    app.dependency_overrides[get_repo] = lambda: mock_repo
    yield
    app.dependency_overrides.clear()

def test_low_stock_success(mock_repo):
    mock_product1 = Mock()
    mock_product1.id = "prod-1"
    mock_product1.name = "Product 1"
    mock_product1.stock = 3
    
    mock_product2 = Mock()
    mock_product2.id = "prod-2"
    mock_product2.name = "Product 2"
    mock_product2.stock = 1
    
    mock_repo.list_low_stock.return_value = [mock_product1, mock_product2]
    
    response = client.get("/api/v1/admin/Product/low-stock?threshold=5")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["product_id"] == "prod-1"
    assert data[0]["stock"] == 3
    mock_repo.list_low_stock.assert_called_once_with(5)

def test_low_stock_non_admin(mock_repo):
    app.dependency_overrides[get_current_user] = mock_non_admin_user
    
    response = client.get("/api/v1/admin/Product/low-stock?threshold=5")
    
    assert response.status_code == 403
    assert "Admin only" in response.json()["detail"]

def test_approve_product_success(mock_repo):
    mock_product = Mock()
    mock_product.id = "prod-1"
    mock_product.name = "Test Product"
    mock_product.stock = 10
    mock_product.is_active = False
    
    mock_repo.get.return_value = mock_product
    mock_repo.save.return_value = None
    
    response = client.post(
        "/api/v1/admin/Product/approve",
        json={"product_id": "prod-1", "approve": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "prod-1"
    assert data["is_active"] == True
    mock_repo.get.assert_called_once_with("prod-1")
    mock_repo.save.assert_called_once()

def test_approve_product_not_found(mock_repo):
    mock_repo.get.return_value = None
    
    response = client.post(
        "/api/v1/admin/Product/approve",
        json={"product_id": "nonexistent", "approve": True}
    )
    
    assert response.status_code == 404
    assert "Product not found" in response.json()["detail"]

def test_approve_product_non_admin(mock_repo):
    app.dependency_overrides[get_current_user] = mock_non_admin_user
    
    response = client.post(
        "/api/v1/admin/Product/approve",
        json={"product_id": "prod-1", "approve": True}
    )
    
    assert response.status_code == 403
    assert "Admin only" in response.json()["detail"]