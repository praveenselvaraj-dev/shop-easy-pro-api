import pytest
from unittest.mock import MagicMock
from datetime import datetime
from src.domain.services.admin_service import AdminService   


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return AdminService(mock_repo)


def test_get_sales_summary(service, mock_repo):
    mock_repo.fetch_sales_summary.return_value = {"total_sales": 1000, "total_orders": 5}

    res = service.get_sales_summary("2025-01-01", "2025-01-31", "token123")

    assert res["total_sales"] == 1000
    mock_repo.fetch_sales_summary.assert_called_once_with(
        datetime.fromisoformat("2025-01-01"),
        datetime.fromisoformat("2025-01-31"),
        "token123"
    )


def test_get_low_stock(service, mock_repo):
    mock_repo.fetch_low_stock.return_value = [
        {"product_id": "p1", "name": "Item", "stock": 2}
    ]

    res = service.get_low_stock(5, "tok123")

    assert len(res) == 1
    mock_repo.fetch_low_stock.assert_called_once_with(5, "tok123")


def test_get_orders(service, mock_repo):
    mock_repo.fetch_orders.return_value = {"total": 10, "page": 1, "size": 20}

    res = service.get_orders(1, 20, "tok123")

    assert res["total"] == 10
    mock_repo.fetch_orders.assert_called_once_with(1, 20, "tok123")


def test_get_order(service, mock_repo):
    mock_repo.fetch_order_details.return_value = {"id": "o1"}

    res = service.get_order("o1", "tok123")

    assert res["id"] == "o1"
    mock_repo.fetch_order_details.assert_called_once_with("o1", "tok123")


def test_approve(service, mock_repo):
    mock_repo.approve_entity.return_value = {"success": True}

    res = service.approve("product", "p1", True, "admin1", "tok123")

    assert res["success"] is True
    mock_repo.approve_entity.assert_called_once_with("product", "p1", True, "admin1", "tok123")
