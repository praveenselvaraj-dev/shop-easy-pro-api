import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from datetime import datetime
from src.main import app
from src.api.routes.order_routes import get_service
from common_auth.dependencies import get_current_user, get_raw_token

client = TestClient(app)

class MockOrder:
    def __init__(self, order_id="order-123", user_id="user-123", total=100.0, status="PAID"):
        self.id = order_id
        self.user_id = user_id
        self.total_amount = total
        self.status = status
        self.created_at = datetime.now()
        self.items = []
    
    def add_item(self, product_id, quantity, price):
        item = Mock()
        item.product_id = product_id
        item.quantity = quantity
        item.price = price
        self.items.append(item)
        return self

def mock_user():
    return {"sub": "user-123", "role": "user"}

def mock_token():
    return "mock-jwt-token"

@pytest.fixture
def mock_service():
    service = Mock()
    service.fetch_product.return_value = {
        "name": "Test Product",
        "image": "http://example.com/product.jpg"
    }
    return service

@pytest.fixture(autouse=True)
def setup_dependencies(mock_service):
    app.dependency_overrides[get_current_user] = mock_user
    app.dependency_overrides[get_raw_token] = mock_token
    app.dependency_overrides[get_service] = lambda: mock_service
    yield
    app.dependency_overrides.clear()

def test_place_order_success(mock_service):
    mock_order = MockOrder()
    mock_order.add_item("prod-1", 2, 50.0)
    mock_service.checkout.return_value = mock_order
    
    response = client.post("/api/v1/Order/checkout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "order-123"
    assert data["user_id"] == "user-123"
    assert data["total_amount"] == 100.0
    assert data["status"] == "PAID"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_name"] == "Test Product"
    
    mock_service.checkout.assert_called_once_with("user-123", "mock-jwt-token")

def test_place_order_empty_cart(mock_service):
    mock_service.checkout.side_effect = Exception("Cart is empty")
    
    response = client.post("/api/v1/Order/checkout")
    
    assert response.status_code == 400
    assert "Cart is empty" in response.json()["detail"]

def test_place_order_payment_failed(mock_service):
    mock_service.checkout.side_effect = Exception("Payment failed")
    
    response = client.post("/api/v1/Order/checkout")
    
    assert response.status_code == 400
    assert "Payment failed" in response.json()["detail"]

def test_place_order_multiple_items(mock_service):
    mock_order = MockOrder(total=250.0)
    mock_order.add_item("prod-1", 2, 50.0)
    mock_order.add_item("prod-2", 1, 150.0)
    
    mock_service.checkout.return_value = mock_order
    mock_service.fetch_product.side_effect = [
        {"name": "Product 1", "image": "http://example.com/p1.jpg"},
        {"name": "Product 2", "image": "http://example.com/p2.jpg"}
    ]
    
    response = client.post("/api/v1/Order/checkout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_amount"] == 250.0
    assert len(data["items"]) == 2
    assert data["items"][0]["product_name"] == "Product 1"
    assert data["items"][1]["product_name"] == "Product 2"

def test_list_orders_success(mock_service):
    order1 = MockOrder("order-1", "user-123", 100.0)
    order1.add_item("prod-1", 1, 100.0)
    
    order2 = MockOrder("order-2", "user-123", 200.0)
    order2.add_item("prod-2", 2, 100.0)
    
    mock_service.list_orders.return_value = [order1, order2]
    
    response = client.get("/api/v1/Order/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "order-1"
    assert data[1]["id"] == "order-2"
    
    mock_service.list_orders.assert_called_once_with("user-123")

def test_list_orders_empty(mock_service):
    mock_service.list_orders.return_value = []
    
    response = client.get("/api/v1/Order/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_get_order_success(mock_service):
    mock_order = MockOrder()
    mock_order.add_item("prod-1", 2, 50.0)
    mock_service.get_order.return_value = mock_order
    
    response = client.get("/api/v1/Order/order-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "order-123"
    assert data["total_amount"] == 100.0
    
    mock_service.get_order.assert_called_once_with("order-123")

def test_get_order_not_found(mock_service):
    mock_service.get_order.return_value = None
    
    response = client.get("/api/v1/Order/nonexistent")
    
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]

def test_get_order_multiple_items(mock_service):
    mock_order = MockOrder(total=300.0)
    mock_order.add_item("prod-1", 1, 100.0)
    mock_order.add_item("prod-2", 2, 100.0)
    
    mock_service.get_order.return_value = mock_order
    mock_service.fetch_product.side_effect = [
        {"name": "Product A", "image": "http://example.com/a.jpg"},
        {"name": "Product B", "image": "http://example.com/b.jpg"}
    ]
    
    response = client.get("/api/v1/Order/order-123")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["quantity"] == 1
    assert data["items"][1]["quantity"] == 2

def test_serialize_order_with_enum_status(mock_service):
    mock_order = MockOrder()
    mock_status = Mock()
    mock_status.value = "PAID"
    mock_order.status = mock_status
    mock_order.add_item("prod-1", 1, 100.0)
    
    mock_service.get_order.return_value = mock_order
    
    response = client.get("/api/v1/Order/order-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PAID"

def test_checkout_product_service_down(mock_service):
    mock_order = MockOrder()
    mock_order.add_item("prod-1", 1, 100.0)
    
    mock_service.checkout.return_value = mock_order
    mock_service.fetch_product.return_value = {
        "name": "Unknown Product",
        "image": None
    }
    
    response = client.post("/api/v1/Order/checkout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["product_name"] == "Unknown Product"
    assert data["items"][0]["product_image"] is None

def test_checkout_service_exception(mock_service):
    mock_service.checkout.side_effect = Exception("Database connection failed")
    
    response = client.post("/api/v1/Order/checkout")
    
    assert response.status_code == 400
    assert "Database connection failed" in response.json()["detail"]

def test_list_orders_user_specific(mock_service):
    order1 = MockOrder("order-1", "user-123", 100.0)
    order1.add_item("prod-1", 1, 100.0)
    
    mock_service.list_orders.return_value = [order1]
    
    response = client.get("/api/v1/Order/")
    
    assert response.status_code == 200
    data = response.json()
    assert all(order["user_id"] == "user-123" for order in data)