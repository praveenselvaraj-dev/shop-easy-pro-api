import pytest
from unittest.mock import Mock, patch, MagicMock
from src.domain.services.order_service import OrderService
from src.infrastructure.database.order_model import Order, OrderItem, OrderStatus

@pytest.fixture
def mock_repo():
    repo = Mock()
    return repo

@pytest.fixture
def order_service(mock_repo):
    return OrderService(mock_repo)

@patch('src.domain.services.order_service.requests.get')
def test_fetch_product_success(mock_get, order_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "prod-1",
        "name": "Test Product",
        "image": "http://example.com/image.jpg",
        "price": 100.0
    }
    mock_get.return_value = mock_response
    
    result = order_service.fetch_product("prod-1")
    
    assert result["name"] == "Test Product"
    assert result["image"] == "http://example.com/image.jpg"
    mock_get.assert_called_once_with("http://localhost:8001/api/v1/Product/prod-1")

@patch('src.domain.services.order_service.requests.get')
def test_fetch_product_service_down(mock_get, order_service):
    mock_get.side_effect = Exception("Connection failed")
    
    result = order_service.fetch_product("prod-1")
    
    assert result["name"] == "Unknown Product"
    assert result["image"] is None

@patch('src.domain.services.order_service.requests.get')
def test_fetch_product_not_found(mock_get, order_service):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = order_service.fetch_product("prod-1")
    
    assert result["name"] == "Unknown Product"
    assert result["image"] is None

@patch('src.domain.services.order_service.requests.get')
def test_fetch_cart_success(mock_get, order_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"product_id": "prod-1", "quantity": 2, "price": 50.0},
            {"product_id": "prod-2", "quantity": 1, "price": 100.0}
        ]
    }
    mock_get.return_value = mock_response
    
    result = order_service.fetch_cart("test-token")
    
    assert len(result) == 2
    assert result[0]["product_id"] == "prod-1"
    assert result[0]["quantity"] == 2
    mock_get.assert_called_once()
    
    call_args = mock_get.call_args
    assert call_args[1]["headers"]["Authorization"] == "Bearer test-token"

@patch('src.domain.services.order_service.requests.get')
def test_fetch_cart_empty(mock_get, order_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response
    
    result = order_service.fetch_cart("test-token")
    
    assert result == []

@patch('src.domain.services.order_service.requests.get')
def test_fetch_cart_service_error(mock_get, order_service):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response
    
    result = order_service.fetch_cart("test-token")
    
    assert result == []

@patch('src.domain.services.order_service.requests.delete')
@patch('src.domain.services.order_service.requests.get')
def test_checkout_success(mock_get, mock_delete, order_service, mock_repo):
    mock_cart_response = Mock()
    mock_cart_response.status_code = 200
    mock_cart_response.json.return_value = {
        "items": [
            {"product_id": "prod-1", "quantity": 2, "price": 50.0},
            {"product_id": "prod-2", "quantity": 1, "price": 100.0}
        ]
    }
    mock_get.return_value = mock_cart_response
    
    mock_order = Mock()
    mock_order.id = "order-123"
    mock_order.user_id = "user-123"
    mock_order.total_amount = 200.0
    mock_order.status = OrderStatus.PAID
    mock_repo.create_order.return_value = mock_order
    
    mock_delete_response = Mock()
    mock_delete_response.status_code = 200
    mock_delete.return_value = mock_delete_response
    
    result = order_service.checkout("user-123", "test-token")
    
    assert result.id == "order-123"
    assert result.total_amount == 200.0
    assert result.status == OrderStatus.PAID
    
    assert mock_repo.create_order.called
    call_args = mock_repo.create_order.call_args[0]
    created_order = call_args[0]
    created_items = call_args[1]
    
    assert created_order.user_id == "user-123"
    assert created_order.total_amount == 200.0
    assert len(created_items) == 2
    
    mock_delete.assert_called_once()
    delete_call_args = mock_delete.call_args
    assert delete_call_args[1]["headers"]["Authorization"] == "Bearer test-token"

@patch('src.domain.services.order_service.requests.get')
def test_checkout_empty_cart(mock_get, order_service, mock_repo):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}
    mock_get.return_value = mock_response
    
    with pytest.raises(Exception) as exc_info:
        order_service.checkout("user-123", "test-token")
    
    assert "Cart is empty" in str(exc_info.value)
    mock_repo.create_order.assert_not_called()

@patch('src.domain.services.order_service.requests.delete')
@patch('src.domain.services.order_service.requests.get')
def test_checkout_calculate_total(mock_get, mock_delete, order_service, mock_repo):
    mock_cart_response = Mock()
    mock_cart_response.status_code = 200
    mock_cart_response.json.return_value = {
        "items": [
            {"product_id": "prod-1", "quantity": 3, "price": 25.5},
            {"product_id": "prod-2", "quantity": 2, "price": 50.0}
        ]
    }
    mock_get.return_value = mock_cart_response
    
    mock_order = Mock()
    mock_repo.create_order.return_value = mock_order
    
    order_service.checkout("user-123", "test-token")
    
    call_args = mock_repo.create_order.call_args[0]
    created_order = call_args[0]
    assert created_order.total_amount == 176.5

def test_list_orders(order_service, mock_repo):
    mock_orders = [Mock(), Mock()]
    mock_repo.get_orders_by_user.return_value = mock_orders
    
    result = order_service.list_orders("user-123")
    
    assert len(result) == 2
    mock_repo.get_orders_by_user.assert_called_once_with("user-123")

def test_list_orders_empty(order_service, mock_repo):
    mock_repo.get_orders_by_user.return_value = []
    
    result = order_service.list_orders("user-123")
    
    assert result == []

def test_get_order(order_service, mock_repo):
    mock_order = Mock()
    mock_order.id = "order-123"
    mock_repo.get_order.return_value = mock_order
    
    result = order_service.get_order("order-123")
    
    assert result.id == "order-123"
    mock_repo.get_order.assert_called_once_with("order-123")

def test_get_order_not_found(order_service, mock_repo):
    mock_repo.get_order.return_value = None
    
    result = order_service.get_order("nonexistent")
    
    assert result is None

@patch('src.domain.services.order_service.requests.delete')
@patch('src.domain.services.order_service.requests.get')
def test_checkout_order_items(mock_get, mock_delete, order_service, mock_repo):
    mock_cart_response = Mock()
    mock_cart_response.status_code = 200
    mock_cart_response.json.return_value = {
        "items": [
            {"product_id": "prod-1", "quantity": 2, "price": 50.0}
        ]
    }
    mock_get.return_value = mock_cart_response
    
    mock_order = Mock()
    mock_repo.create_order.return_value = mock_order
    
    order_service.checkout("user-123", "test-token")
    
    call_args = mock_repo.create_order.call_args[0]
    order_items = call_args[1]
    
    assert len(order_items) == 1
    assert order_items[0].product_id == "prod-1"
    assert order_items[0].quantity == 2
    assert order_items[0].price == 50.0

@patch('src.domain.services.order_service.requests.delete')
@patch('src.domain.services.order_service.requests.get')
def test_checkout_payment_success(mock_get, mock_delete, order_service, mock_repo):
    """Test that payment is simulated as successful"""
    mock_cart_response = Mock()
    mock_cart_response.status_code = 200
    mock_cart_response.json.return_value = {
        "items": [{"product_id": "prod-1", "quantity": 1, "price": 100.0}]
    }
    mock_get.return_value = mock_cart_response
    
    mock_order = Mock()
    mock_order.status = OrderStatus.PAID
    mock_repo.create_order.return_value = mock_order
    
    result = order_service.checkout("user-123", "test-token")
    
    call_args = mock_repo.create_order.call_args[0]
    created_order = call_args[0]
    assert created_order.status == OrderStatus.PAID