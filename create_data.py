import random
from uuid import uuid4
from database.db import DBSession
from database.session import provide_session
from modules.courses.models import CMICourse, CMIEnrollment
from modules.statements.models import CMIStatement
from modules.users.models import User
from modules.users.utils import get_password_hash
import string

import asyncio


class DataCreator:
    @provide_session
    async def _create_users(self, session: DBSession) -> list[User]:
        users = [
            User(
                id=uuid4(),
                email=f"test_{str(index)}@gmail.com",
                password=get_password_hash("password"),
            )
            for index in range(5)
        ]

        session.add_all(users)
        await session.commit()

        return users

    @provide_session
    async def _create_courses(self, session: DBSession) -> list[CMICourse]:
        courses = [
            CMICourse(
                id=uuid4(),
                title=f"Course_{str(index)}",
                description=f"Description_{str(index)}",
                organization_id=uuid4(),
            )
            for index in range(5)
        ]

        session.add_all(courses)
        await session.commit()

        return courses

    @provide_session
    async def _assign_courses(
        self, users: list[User], courses: list[CMICourse], session: DBSession
    ) -> list[CMIEnrollment]:
        enrollments = []

        for user, course in zip(users, courses):
            enrollment = CMIEnrollment(
                id=uuid4(),
                user_id=user.id,
                course_id=course.id,
            )

            enrollments.append(enrollment)

        session.add_all(enrollments)
        await session.commit()

        return enrollments

    @provide_session
    async def _set_statements(
        self, enrollments: list[CMIEnrollment], session: DBSession
    ) -> None:
        letters = string.ascii_lowercase + string.digits
        for e in enrollments:
            generate_pass = "".join([random.choice(letters) for _ in range(100)])
            statement = CMIStatement(
                id=uuid4(), statements={"status": True, "data": generate_pass}
            )
            session.add(statement)
            e.statement_id = statement.id
            session.add(e)
            await session.commit()

    async def generate(self) -> None:
        users = await self._create_users()
        courses = await self._create_courses()
        enrollments = await self._assign_courses(users, courses)
        await self._set_statements(enrollments)


if __name__ == "__main__":
    generator = DataCreator()
    asyncio.run(generator.generate())
