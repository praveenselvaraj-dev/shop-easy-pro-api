import pytest
from fastapi.testclient import TestClient
from main import app  
from domain.services.auth_service import AuthService
from unittest.mock import MagicMock
from domain.entities.user import User
from utils.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from api.dependencies import get_auth_service
@pytest.fixture
def mock_auth_service():
    return MagicMock()

@pytest.fixture
def client(mock_auth_service):
    app.dependency_overrides = {}
    app.dependency_overrides[
        get_auth_service
    ] = lambda: mock_auth_service

    return TestClient(app)


def test_register_api_success(client, mock_auth_service):
    fake_user = User(
        id=1,
        username="john",
        email="john@example.com",
        role="user",
        is_active=True,
        is_verified=True,
        created_at="2024-01-01"
    )

    mock_auth_service.register.return_value = {"data": fake_user}

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "john",
            "email": "john@example.com",
            "password": "StrongPass123",
            "role": "user"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "john@example.com"


def test_register_existing_email(client, mock_auth_service):
    mock_auth_service.register.side_effect = UserAlreadyExistsError("Email exists")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "john",
            "email": "john@example.com",
            "password": "StrongPass123",
            "role": "user"
        }
    )

    assert response.status_code == 400


def test_login_success(client, mock_auth_service):
    fake_user = User(
        id=1, username="john", email="john@example.com",
        role="user", is_active=True, is_verified=True, created_at="2024-01-01"
    )

    mock_auth_service.login.return_value = {
        "access_token": "abcd",
        "token_type": "bearer",
        "user": fake_user
    }

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "john", "password": "StrongPass123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "abcd"
    assert body["user"]["email"] == "john@example.com"


def test_login_invalid(client, mock_auth_service):
    mock_auth_service.login.side_effect = InvalidCredentialsError("Invalid")

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "john", "password": "wrong"}
    )

    assert response.status_code == 401
