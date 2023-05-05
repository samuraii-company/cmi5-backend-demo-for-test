from uuid import uuid4
from fastapi import Depends
from sqlalchemy import and_, select
from database.db import DBSession
from database.session import get_session, provide_session
from modules.users.models import User
from .utils import get_password_hash


class UserService:
    model: User = User

    def __init__(self, session: DBSession = Depends(get_session)):
        self.session = session

    async def create(self, data: dict) -> User:
        user = User(
            id=uuid4(),
            email=data.get("email"),
            password=get_password_hash(data.get("password")),
            # organization_id="ebbc58b4db644e93bdfbe493534e847c",  # FAKE FIELD DATA
        )

        self.session.add(user)
        await self.session.commit()
        return user

    async def get_by_email(self, email: str) -> User | None:
        user = (
            await self.session.execute(
                select(self.model).where(
                    and_(self.model.email == email, self.model.deleted_at.is_(None))
                )
            )
        ).scalar()

        return user

    async def get_all(self) -> list[User | None]:
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
