from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from modules.users.schema import UserCreate, UserRead
from modules.users.services import UserService


users_router = APIRouter(tags=["users"], prefix="/api/users")


@users_router.post("", response_model=UserRead)
async def create_user(
    data: UserCreate,
    user_service: UserService = Depends(UserService),
):
    """Create a new user"""

    user = await user_service.get_by_email(data.email)

    if user:
        raise HTTPException(detail="Пользователь уже есть", status_code=400)

    user = await user_service.create(data.dict())

    return user


@users_router.get("", response_model=list[UserRead])
async def create_user(
    user_service: UserService = Depends(UserService),
):
    """Get all not deleted users"""

    users = await user_service.get_all()

    return users


@users_router.get("/email/{email}", response_model=UserRead)
async def get_by_email(
    email: str,
    user_service: UserService = Depends(UserService),
):
    """Get user by email"""

    user = await user_service.get_by_email(email)

    if not user:
        raise HTTPException(detail="Юзера нет", status_code=404)

    return user
