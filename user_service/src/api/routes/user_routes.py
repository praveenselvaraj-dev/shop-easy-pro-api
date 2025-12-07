from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.domain.services.user_service import UserService
from src.api.schemas.user_schema import UserResponse, UserUpdateRequest
from src.api.dependencies import get_user_service, get_current_user, require_admin
from src.utils.exceptions import UserNotFoundError

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    admin = Depends(require_admin)
):
    return user_service.get_all_users(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    # try:
        return user_service.get_user_by_id(user_id)
    # except UserNotFoundError as e:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    if current_user.id != user_id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    try:
        update_data = request.dict(exclude_unset=True)
        return user_service.update_user(user_id, **update_data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    admin = Depends(require_admin)
):
    try:
        user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
