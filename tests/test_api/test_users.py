from uuid import uuid4

from sqlalchemy import and_, select
from modules.users.models import User
from shared.utils import matches


class TestUsersAPI:
    def setup(self):
        self.user = User(id=uuid4(), email="test@gmail.com", password="password")

    async def test_get_all_users(self, db_session, api_app, client):
        async with db_session() as session:
            session.add(self.user)
            await session.commit()

        response = await client.get(
            api_app.url_path_for("users:get_all_users"),
        )

        assert response.status_code == 200
        assert matches(
            response.json(),
            [
                {
                    "id": ...,
                    "email": "test@gmail.com",
                }
            ],
        )

    async def test_create_user(self, api_app, client):
        response = await client.post(
            api_app.url_path_for("users:create_user"),
            json=dict(email="test2@gmail.com", password="password"),
        )

        assert response.status_code == 200
        assert matches(
            response.json(),
            {
                "id": ...,
                "email": "test2@gmail.com",
            },
        )

    async def test_create_user__already_exist(self, db_session, api_app, client):
        async with db_session() as session:
            session.add(self.user)
            await session.commit()

        response = await client.post(
            api_app.url_path_for("users:create_user"),
            json=dict(email="test@gmail.com", password="password"),
        )

        assert response.status_code == 400

    async def test_get_user_by_email(self, db_session, api_app, client):
        async with db_session() as session:
            session.add(self.user)
            await session.commit()

        response = await client.get(
            api_app.url_path_for("users:get_by_email", email=self.user.email),
        )

        assert response.status_code == 200
        assert matches(
            response.json(),
            {
                "id": ...,
                "email": "test@gmail.com",
            },
        )

    async def test_get_user_by_email__not_found(self, api_app, client):
        response = await client.get(
            api_app.url_path_for("users:get_by_email", email="t@yandex.ru"),
        )

        assert response.status_code == 404

    async def test_delete_user(self, db_session, api_app, client):
        async with db_session() as session:
            session.add(self.user)
            await session.commit()

        response = await client.delete(
            api_app.url_path_for("users:delete_user", user_id=self.user.id),
        )

        assert response.status_code == 204

        async with db_session() as session:
            user = (
                await session.execute(
                    select(User).where(
                        and_(
                            User.id == self.user.id,
                            User.deleted_at.is_(None),
                        )
                    )
                )
            ).scalar()

        assert not user

    async def test_delete_user__not_found(self, db_session, api_app, client):
        async with db_session() as session:
            session.add(self.user)
            await session.commit()

        response = await client.delete(
            api_app.url_path_for("users:delete_user", user_id=uuid4()),
        )

        assert response.status_code == 404
