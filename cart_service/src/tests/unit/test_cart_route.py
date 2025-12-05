import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from domain.services.cart_service import CartService
from common_auth.dependencies import get_current_user, get_raw_token
from src.api.routes.cart_route import get_service

client = TestClient(app)

# ---------------------------
# Fake User + Fake Token
# ---------------------------
def fake_user():
    return {"sub": "U1", "role": "user"}

def fake_token():
    return "FAKE_TOKEN"

# ---------------------------
# Override dependencies
# ---------------------------
@pytest.fixture
def mock_service():
    mock = MagicMock(spec=CartService)

    app.dependency_overrides[get_current_user] = fake_user
    app.dependency_overrides[get_raw_token] = fake_token
    app.dependency_overrides[get_service] = lambda: mock

    yield mock
    app.dependency_overrides.clear()


# ============================================================
# GET /cart
# ============================================================
def test_get_cart(mock_service):
    item = MagicMock()
    item.id = "1"
    item.product_id = "P1"
    item.quantity = 2
    item.price = 100.0

    # Service returns cart items
    mock_service.get_cart.return_value = [item]

    # Product details lookup
    mock_service.fetch_product_details.return_value = {
        "name": "Product 1",
        "image": "img.jpg"
    }

    res = client.get("/api/v1/Cart/")
    assert res.status_code == 200

    body = res.json()
    assert body["items"][0]["product_id"] == "P1"
    assert body["items"][0]["name"] == "Product 1"
    assert body["items"][0]["total"] == 200


# ============================================================
# POST /cart
# ============================================================
def test_add_to_cart(mock_service):
    item = MagicMock()
    item.id = "1"
    item.product_id = "P1"
    item.quantity = 2
    item.price = 100.0

    mock_service.add_to_cart.return_value = item

    mock_service.fetch_product_details.return_value = {
        "name": "Product 1",
        "image": "img.jpg"
    }

    res = client.post("/api/v1/Cart/", json={
        "product_id": "P1",
        "quantity": 2
    })

    assert res.status_code == 200
    data = res.json()

    assert data["product_id"] == "P1"
    assert data["name"] == "Product 1"
    assert data["total"] == 200


# ============================================================
# PUT /cart/{item_id}
# ============================================================
def test_update_quantity(mock_service):
    item = MagicMock()
    item.id = "1"
    item.product_id = "P1"
    item.quantity = 5
    item.price = 100.0

    mock_service.update_quantity.return_value = item
    mock_service.fetch_product_details.return_value = {
        "name": "Product 1",
        "image": "img.jpg"
    }

    res = client.put("/api/v1/Cart/1", json={"quantity": 5})

    assert res.status_code == 200
    data = res.json()

    assert data["quantity"] == 5
    assert data["total"] == 500


# ============================================================
# DELETE /cart/{item_id}
# ============================================================
def test_delete_item(mock_service):
    res = client.delete("/api/v1/Cart/1")
    assert res.status_code == 200
    assert res.json()["message"] == "Item removed successfully"


# ============================================================
# DELETE /cart
# ============================================================
def test_clear_cart(mock_service):
    res = client.delete("/api/v1/Cart/")
    assert res.status_code == 200
    assert res.json()["message"] == "Cart cleared successfully"
