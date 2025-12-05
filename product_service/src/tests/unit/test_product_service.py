import pytest
from unittest.mock import MagicMock
from src.domain.services.product_service import ProductService


def test_create_product():
    repo = MagicMock()
    service = ProductService(repo)

    data = {"name": "Test", "price": 100}
    repo.create.return_value = {"id": 1, **data}

    result = service.create(data)

    assert result["id"] == 1
    repo.create.assert_called_once_with(data)


def test_get_product():
    repo = MagicMock()
    service = ProductService(repo)

    repo.get_by_id.return_value = {"id": 1, "name": "Test"}

    result = service.get("1")

    assert result["id"] == 1
    repo.get_by_id.assert_called_once_with("1")


def test_update_product_with_image():
    repo = MagicMock()
    service = ProductService(repo)

    image = MagicMock()
    data = {"name": "Updated"}

    service.update("1", data, image)

    assert data["image"] == image
    repo.update.assert_called_once()


def test_update_product_no_image():
    repo = MagicMock()
    service = ProductService(repo)

    data = {"price": 200}

    service.update("1", data, None)

    repo.update.assert_called_once_with("1", data)


def test_delete_product():
    repo = MagicMock()
    service = ProductService(repo)

    repo.delete.return_value = True

    assert service.delete("1") is True
    repo.delete.assert_called_once_with("1")
