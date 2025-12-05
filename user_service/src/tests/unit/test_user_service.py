import pytest
from unittest.mock import MagicMock
from src.domain.services.user_service import UserService
from src.domain.entities.user import User
from src.utils.exceptions import UserNotFoundError


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return UserService(mock_repo)


def test_get_user_by_id_success(service, mock_repo):
    user = User(id=1, username="john", email="john@example.com",
                role="user", is_active=True, is_verified=True, created_at="2024-01-01")
    
    mock_repo.get_by_id.return_value = user

    result = service.get_user_by_id(1)

    assert result == user
    mock_repo.get_by_id.assert_called_once_with(1)


def test_get_user_by_id_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        service.get_user_by_id(1)


def test_get_all_users(service, mock_repo):
    users = [
        User(id=1, username="john", email="john@example.com", role="user",
             is_active=True, is_verified=True, created_at="2024-01-01")
    ]
    
    mock_repo.get_all.return_value = users

    result = service.get_all_users(0, 100)

    assert result == users
    mock_repo.get_all.assert_called_once_with(0, 100)


def test_update_user_success(service, mock_repo):
    user = User(id=1, username="updated", email="john@example.com",
                role="user", is_active=True, is_verified=True, created_at="2024-01-01")
    
    mock_repo.update.return_value = user

    result = service.update_user(1, username="updated")

    assert result == user
    mock_repo.update.assert_called_once_with(1, username="updated")


def test_update_user_not_found(service, mock_repo):
    mock_repo.update.return_value = None

    with pytest.raises(UserNotFoundError):
        service.update_user(1, username="newname")


def test_delete_user_success(service, mock_repo):
    mock_repo.delete.return_value = True

    result = service.delete_user(1)

    assert result is True
    mock_repo.delete.assert_called_once_with(1)


def test_delete_user_not_found(service, mock_repo):
    mock_repo.delete.return_value = False

    with pytest.raises(UserNotFoundError):
        service.delete_user(1)
