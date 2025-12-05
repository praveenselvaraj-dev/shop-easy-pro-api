from fastapi import APIRouter, Depends, HTTPException, status
from domain.services.auth_service import AuthService
from api.schemas.auth_schema import RegisterRequest, LoginRequest, TokenResponse,RegisterResponse
from api.dependencies import get_auth_service
from utils.exceptions import UserAlreadyExistsError, InvalidCredentialsError
import traceback

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        result = auth_service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role
        )
        print(f"User: {result['data']}")
        return  {
            "status": "success",
            "message": "User registered successfully.",
            "data": {
                "id": result["data"].id,
                "username": result["data"].username,
                "email": result["data"].email,
                "createdAt": result["data"].created_at
            }
        }
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
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
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
