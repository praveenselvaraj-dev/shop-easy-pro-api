import pytest
from unittest.mock import MagicMock, patch
from domain.services.cart_service import CartService
from utils.exceptions import ProductNotFound
PRODUCT_RESPONSE = {
    "price": 100,
    "name": "Test Product",
    "image": "test.jpg"
}

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    return repo

@pytest.fixture
def service(mock_repo):
    return CartService(mock_repo)

# --------------------------
# 1) fetch_product_price
# --------------------------
@patch("domain.services.cart_service.requests.get")
def test_fetch_product_price_success(mock_get, service):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = PRODUCT_RESPONSE

    result = service.fetch_product_price("P1")

    assert result["price"] == 100
    assert result["name"] == "Test Product"

@patch("domain.services.cart_service.requests.get")
def test_fetch_product_price_not_found(mock_get, service):
    mock_get.return_value.status_code = 404

    with pytest.raises(ProductNotFound):
        service.fetch_product_price("BAD")


# --------------------------
# 2) add_to_cart (new item)
# --------------------------
@patch("domain.services.cart_service.requests.post")
@patch("domain.services.cart_service.requests.get")
def test_add_to_cart_new_item(mock_get, mock_post, service, mock_repo):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = PRODUCT_RESPONSE

    mock_post.return_value.status_code = 200
    mock_repo.get_item.return_value = None

    mock_repo.add_item.return_value = MagicMock(
        id="1",
        product_id="P1",
        quantity=2,
        price=100,
        user_id="U1"
    )

    item = service.add_to_cart("U1", "P1", 2)

    mock_repo.add_item.assert_called_once()
    assert item.product_id == "P1"

# --------------------------
# 3) add_to_cart (increase quantity)
# --------------------------
@patch("domain.services.cart_service.requests.post")
@patch("domain.services.cart_service.requests.get")
def test_add_to_cart_existing_item(mock_get, mock_post, service, mock_repo):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = PRODUCT_RESPONSE
    mock_post.return_value.status_code = 200

    mock_repo.get_item.return_value = MagicMock(
        id="1",
        product_id="P1",
        quantity=1,
        price=100,
        user_id="U1"
    )

    updated_item = MagicMock(
        id="1",
        product_id="P1",
        quantity=3,
        price=100
    )

    mock_repo.update_item.return_value = updated_item

    item = service.add_to_cart("U1", "P1", 2)

    assert item.quantity == 3
    mock_repo.update_item.assert_called_once()

# --------------------------
# 4) update_quantity
# --------------------------
@patch("domain.services.cart_service.requests.post")
def test_update_quantity_increase(mock_post, service, mock_repo):
    mock_repo.get_item_by_id.return_value = MagicMock(
        id="1",
        product_id="P1",
        quantity=1,
        user_id="U1"
    )

    mock_post.return_value.status_code = 200

    updated = MagicMock(quantity=3)
    mock_repo.update_item.return_value = updated

    result = service.update_quantity("1", 3, "U1")
    assert result.quantity == 3

# --------------------------
# 5) delete_item
# --------------------------
def test_delete_item(service, mock_repo):
    mock_repo.get_item_by_id.return_value = MagicMock(
        id="1",
        product_id="P1",
        quantity=2,
        user_id="U1"
    )

    service.delete_item("1", "U1")

    mock_repo.delete_item.assert_called_once()

# --------------------------
# 6) clear_cart
# --------------------------
def test_clear_cart(service, mock_repo):
    mock_repo.get_cart.return_value = [
        MagicMock(product_id="P1", quantity=2),
        MagicMock(product_id="P2", quantity=1)
    ]

    service.clear_cart("U1")

    mock_repo.clear_cart.assert_called_once()
