import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from src.main import app
from src.domain.entities.user import User
from src.api.dependencies import get_user_service, get_current_user, require_admin
from src.utils.exceptions import UserNotFoundError


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_user_service():
    return MagicMock()


@pytest.fixture
def fake_user():
    return User(
        id=1,
        username="john",
        email="john@example.com",
        role="admin",
        is_active=True,
        is_verified=True,
        created_at="2024-01-01"
    )


@pytest.fixture(autouse=True)
def override_dependencies(mock_user_service, fake_user):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = lambda: fake_user
    app.dependency_overrides[require_admin] = lambda: True  # always admin
    yield
    app.dependency_overrides = {}


def test_get_me(client, fake_user):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == fake_user.email


def test_get_all_users(client, mock_user_service, fake_user):
    mock_user_service.get_all_users.return_value = [fake_user]

    response = client.get("/api/v1/users/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_success(client, mock_user_service, fake_user):
    mock_user_service.get_user_by_id.return_value = fake_user

    response = client.get("/api/v1/users/1")

    assert response.status_code == 200
    assert response.json()["username"] == "john"


def test_get_user_not_found(client, mock_user_service):
    mock_user_service.get_user_by_id.side_effect = UserNotFoundError("Not found")

    response = client.get("/api/v1/users/999")

    assert response.status_code == 404


def test_update_user_success(client, mock_user_service, fake_user):
    mock_user_service.update_user.return_value = fake_user

    response = client.put("/api/v1/users/1", json={"username": "newname"})

    assert response.status_code == 200
    assert response.json()["username"] == "john"  

def test_update_user_not_found(client, mock_user_service):
    mock_user_service.update_user.side_effect = UserNotFoundError("Not found")

    response = client.put("/api/v1/users/1", json={"username": "boom"})

    assert response.status_code == 404


def test_delete_user_success(client, mock_user_service):
    mock_user_service.delete_user.return_value = True

    response = client.delete("/api/v1/users/1")

    assert response.status_code == 204


def test_delete_user_not_found(client, mock_user_service):
    mock_user_service.delete_user.side_effect = UserNotFoundError("Not found")

    response = client.delete("/api/v1/users/999")

    assert response.status_code == 404
