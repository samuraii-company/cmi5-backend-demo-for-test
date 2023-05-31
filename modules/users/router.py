from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from modules.users.schema import UserCreate, UserRead
from modules.users.services import UserService

users_router = APIRouter(tags=["users"], prefix="/api/users")


@users_router.post("", response_model=UserRead, name="users:create_user")
async def create_user(
    data: UserCreate,
    user_service: UserService = Depends(UserService),
):
    """Create a new user"""

    user = await user_service.get_by_email(data.email)

    if user:
        raise HTTPException(detail="User already exist", status_code=400)

    user = await user_service.create(data.dict())

    return user


@users_router.get("", response_model=list[UserRead], name="users:get_all_users")
async def get_all_users(
    user_service: UserService = Depends(UserService),
):
    """Get all not deleted users"""

    users = await user_service.get_all()

    return users


@users_router.get("/email/{email}", response_model=UserRead, name="users:get_by_email")
async def get_by_email(
    email: str,
    user_service: UserService = Depends(UserService),
):
    """Get user by email"""

    user = await user_service.get_by_email(email)

    if not user:
        raise HTTPException(detail="User not found", status_code=404)

    return user


@users_router.delete("{user_id}", response_model=UserRead, name="users:delete_user")
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(UserService),
):
    """Delete user by user id"""

    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(detail="User not found", status_code=404)

    await user_service.delete(user)

    return Response(status_code=204)
