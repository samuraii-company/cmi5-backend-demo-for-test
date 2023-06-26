import datetime
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import and_, select, update

from database.db import DBSession
from database.session import get_session
from modules.users.models import User

from .utils import get_password_hash


class UserService:
    model: User = User

    def __init__(self, session: DBSession = Depends(get_session)):
        self.session = session

    async def create(self, data: dict) -> User:
        """Create a new user

        Args:
            data (dict): user data

        Returns:
            User: yser instance
        """
        user = User(
            id=uuid4(),
            email=data.get("email"),
            password=get_password_hash(data.get("password")),
        )

        self.session.add(user)
        await self.session.commit()
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email: Deprecated method

        Args:
            email (str): email

        Returns:
            User | None: user instance or none
        """
        user = (
            await self.session.execute(
                select(self.model).where(
                    and_(
                        self.model.email == email,
                        self.model.deleted_at.is_(None),
                    )
                )
            )
        ).scalar()

        return user

    async def delete(self, user: User) -> None:
        """Delete user

        Args:
            user (User): user instance
        """
        query = (
            update(self.model)
            .where(
                and_(
                    self.model.deleted_at.is_(None),
                    self.model.id == user.id,
                )
            )
            .values(deleted_at=datetime.datetime.utcnow())
        )

        await self.session.execute(query)

    async def get_all(self) -> list[User | None]:
        """Get all users

        Returns:
            list[User | None]: list users or empty list
        """
        user = (
            (
                await self.session.execute(
                    select(self.model).where(self.model.deleted_at.is_(None))
                )
            )
            .scalars()
            .all()
        )

        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by id

        Args:
            user_id (UUID): user id

        Returns:
            User | None: user instance or none
        """
        user = (
            await self.session.execute(
                select(self.model).where(
                    and_(
                        self.model.id == user_id,
                        self.model.deleted_at.is_(None),
                    )
                )
            )
        ).scalar()

        return user
