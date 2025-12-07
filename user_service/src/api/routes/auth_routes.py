from fastapi import APIRouter, Depends, status
from domain.services.auth_service import AuthService
from api.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse, RegisterResponse
from api.dependencies import get_auth_service
from utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""

    # Let exceptions bubble up to middleware
    result = auth_service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        role=request.role
    )

    return {
        "status": "success",
        "message": "User registered successfully.",
        "data": {
            "id": result["data"].id,
            "username": result["data"].username,
            "email": result["data"].email,
            "createdAt": result["data"].created_at
        }
    }


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user — no try/except here"""

    # Let InvalidCredentialsError go to middleware
    result = auth_service.login(username=request.username, password=request.password)

    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": {
            "id": result["user"].id,
            "username": result["user"].username,
            "email": result["user"].email,
            "role": result["user"].role
        }
    }
