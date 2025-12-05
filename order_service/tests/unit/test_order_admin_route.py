import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import datetime
from src.main import app
from src.api.routes.order_admin_route import get_repo
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
    """Setup dependency overrides for all tests"""
    app.dependency_overrides[get_current_user] = mock_admin_user
    app.dependency_overrides[get_repo] = lambda: mock_repo
    yield
    app.dependency_overrides.clear()

def test_admin_sales_with_dates(mock_repo):
    mock_summary = {
        "total_sales": 5000.0,
        "total_orders": 25,
        "from_date": "2024-01-01",
        "to_date": "2024-01-31"
    }
    mock_repo.sales_summary.return_value = mock_summary
    
    response = client.get(
        "/api/v1/admin/Order/sales?from_date=2024-01-01T00:00:00&to_date=2024-01-31T23:59:59"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_sales"] == 5000.0
    assert data["total_orders"] == 25
    
    call_args = mock_repo.sales_summary.call_args[0]
    assert isinstance(call_args[0], datetime)
    assert isinstance(call_args[1], datetime)

def test_admin_sales_no_dates(mock_repo):
    mock_summary = {
        "total_sales": 10000.0,
        "total_orders": 50
    }
    mock_repo.sales_summary.return_value = mock_summary
    
    response = client.get("/api/v1/admin/Order/sales")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_sales"] == 10000.0
    assert data["total_orders"] == 50
    
    mock_repo.sales_summary.assert_called_once_with(None, None)

def test_admin_sales_only_from_date(mock_repo):
    mock_summary = {
        "total_sales": 3000.0,
        "total_orders": 15
    }
    mock_repo.sales_summary.return_value = mock_summary
    
    response = client.get("/api/v1/admin/Order/sales?from_date=2024-01-01T00:00:00")
    
    assert response.status_code == 200
    call_args = mock_repo.sales_summary.call_args[0]
    assert isinstance(call_args[0], datetime)
    assert call_args[1] is None

def test_admin_sales_only_to_date(mock_repo):
    mock_summary = {
        "total_sales": 2000.0,
        "total_orders": 10
    }
    mock_repo.sales_summary.return_value = mock_summary
    
    response = client.get("/api/v1/admin/Order/sales?to_date=2024-01-31T23:59:59")
    
    assert response.status_code == 200
    call_args = mock_repo.sales_summary.call_args[0]
    assert call_args[0] is None
    assert isinstance(call_args[1], datetime)

def test_admin_sales_non_admin(mock_repo):
    app.dependency_overrides[get_current_user] = mock_non_admin_user
    
    response = client.get("/api/v1/admin/Order/sales")
    
    assert response.status_code == 403
    assert "Admin only" in response.json()["detail"]
    mock_repo.sales_summary.assert_not_called()

def test_admin_sales_invalid_date_format(mock_repo):
    response = client.get("/api/v1/admin/Order/sales?from_date=invalid-date")
    
    assert response.status_code == 500 or response.status_code == 400

def test_admin_sales_empty_result(mock_repo):
    mock_summary = {
        "total_sales": 0.0,
        "total_orders": 0
    }
    mock_repo.sales_summary.return_value = mock_summary
    
    response = client.get("/api/v1/admin/Order/sales")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_sales"] == 0.0
    assert data["total_orders"] == 0