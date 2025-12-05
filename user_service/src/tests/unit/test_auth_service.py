import pytest
from unittest.mock import MagicMock
from domain.services.auth_service import AuthService
from utils.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from domain.entities.user import User

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def auth_service(mock_repo):
    return AuthService(mock_repo)


def test_register_success(auth_service, mock_repo):
    
    mock_repo.get_by_email.return_value = None
    mock_repo.get_by_username.return_value = None

    fake_user = User(
        id=1, username="john", email="john@example.com",
        role="user", is_active=True, is_verified=True, created_at="2024-01-01"
    )
    mock_repo.create.return_value = fake_user

    result = auth_service.register(
        username="john",
        email="john@example.com",
        password="StrongPass123",
        role="user"
    )

    assert result["data"].email == "john@example.com"
    assert result["data"].username == "john"
    mock_repo.create.assert_called_once()


def test_register_email_exists(auth_service, mock_repo):
   

    mock_repo.get_by_email.return_value = True  # exists

    with pytest.raises(UserAlreadyExistsError):
        auth_service.register("john", "john@example.com", "StrongPass123", "user")


def test_login_success(auth_service, mock_repo, monkeypatch):
   

    fake_user = User(
        id=1, username="john", email="john@example.com",
        role="user", is_active=True, is_verified=True, created_at="2024-01-01"
    )
    mock_repo.get_by_username.return_value = fake_user
    mock_repo.get_password_hash.return_value = "hashed_pass"

    
    monkeypatch.setattr(
        "domain.services.auth_service.verify_password",
        lambda pwd, hash: True
    )

    result = auth_service.login("john", "StrongPass123")

    assert result["user"].username == "john"
    assert result["token_type"] == "bearer"


def test_login_invalid_username(auth_service, mock_repo):
    mock_repo.get_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        auth_service.login("unknown", "password")


def test_login_invalid_password(auth_service, mock_repo, monkeypatch):
    fake_user = User(
        id=1, username="john", email="john@example.com",
        role="user", is_active=True, is_verified=True, created_at="2024-01-01"
    )

    mock_repo.get_by_username.return_value = fake_user
    mock_repo.get_password_hash.return_value = "db_hash"

    monkeypatch.setattr(
        "domain.services.auth_service.verify_password",
        lambda pwd, hash: False
    )

    with pytest.raises(InvalidCredentialsError):
        auth_service.login("tony", "SecurePass123")
