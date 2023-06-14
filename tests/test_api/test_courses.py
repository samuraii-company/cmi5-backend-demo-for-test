import io
import os
from uuid import uuid4

from modules.users.models import User
from modules.courses.models import CMICourse, CMIEnrollment
from modules.statements.models import CMIStatement
from shared.utils import matches

ARCHIVE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../resources/scorm.zip",
)


class TestCourseAPI:
    def setup(self):
        self.course = CMICourse(
            id=uuid4(),
            title="string",
            description="string",
            organization_id=uuid4(),
            file_link="/courses/string.zip",
        )

        self.user = User(id=uuid4(), email="test@gmail.com", password="password")
        self.statements = CMIStatement(id=uuid4(), statements=dict(status="ok"))
        self.enrollment = CMIEnrollment(
            id=uuid4(),
            course_id=self.course.id,
            user_id=self.user.id,
            statement_id=self.statements.id,
        )

    async def test_get_courses(self, db_session, api_app, client):
        async with db_session() as session:
            session.add_all(
                (
                    self.course,
                    self.user,
                    self.statements,
                    self.enrollment,
                )
            )
            await session.commit()

        response = await client.get(
            api_app.url_path_for("courses:get_cmi5_all_courses"),
        )

        assert response.status_code == 200
        assert matches(
            response.json(),
            [
                {
                    "id": str(self.course.id),
                    "title": self.course.title,
                    "description": self.course.description,
                    "file_link": ...,
                }
            ],
        )

    async def test_get_course_by_id(self, db_session, api_app, client):
        async with db_session() as session:
            session.add_all(
                (
                    self.course,
                    self.user,
                    self.statements,
                    self.enrollment,
                )
            )
            await session.commit()

        response = await client.get(
            api_app.url_path_for("courses:get_cmi5_course", course_id=self.course.id),
        )

        assert response.status_code == 200
        assert matches(
            response.json(),
            {
                "id": str(self.course.id),
                "title": self.course.title,
                "description": self.course.description,
                "file_link": ...,
                "users": [
                    {
                        "id": str(self.user.id),
                        "email": self.user.email,
                    }
                ],
            },
        )

    async def test_get_course_by_id__not_found(self, api_app, client):
        response = await client.get(
            api_app.url_path_for("courses:get_cmi5_course", course_id=uuid4()),
        )

        assert response.status_code == 404

    async def test_create_course(self, api_app, client, mocker):
        # INFO: not mockeing extract_zip and delete_folder, becouse need tests this functional
        with open(str(ARCHIVE_PATH), "rb") as f:
            fake_file = f.read()
            scorm_archive = {"file": io.BytesIO(fake_file)}

        mocker.patch(
            "storage.storage.LocalStorage.save_course_folder",
            return_value=f"courses/{str(uuid4())}.zip",
        )

        response = await client.post(
            api_app.url_path_for("courses:create_cmi5_course"),
            files=scorm_archive,
            data={"title": "string2", "description": "string2"},
        )

        assert response.status_code == 200

        assert matches(
            response.json(),
            {
                "id": str(response.json()["id"]),
                "title": "string2",
                "description": "string2",
                "file_link": ...,
                "users": [],
            },
        )

    async def test_enrollment_create(self, db_session, api_app, client):
        course = CMICourse(
            id=uuid4(),
            title="string",
            description="string",
            organization_id=uuid4(),
            file_link="/courses/string2.zip",
        )

        user = User(id=uuid4(), email="test3@gmail.com", password="password")

        async with db_session() as session:
            session.add_all((course, user))
            await session.commit()

        response = await client.post(
            api_app.url_path_for("courses:set_enrollment"),
            json={"course_id": str(course.id), "user_id": str(user.id)},
        )

        assert response.status_code == 200

        assert matches(
            response.json(),
            {
                "course": {
                    "id": ...,
                    "title": course.title,
                    "description": course.description,
                    "file_link": ...,
                },
                "user": {
                    "id": ...,
                    "email": user.email,
                },
            },
        )

    async def test_enrollment_create__already_created(
        self, db_session, api_app, client
    ):
        async with db_session() as session:
            session.add_all(
                (
                    self.course,
                    self.user,
                    self.statements,
                    self.enrollment,
                )
            )
            await session.commit()

        response = await client.post(
            api_app.url_path_for("courses:set_enrollment"),
            json={"course_id": str(self.course.id), "user_id": str(self.user.id)},
        )

        assert response.status_code == 400

    async def test_get_all_statements(self, db_session, api_app, client):
        async with db_session() as session:
            session.add_all(
                (
                    self.course,
                    self.user,
                    self.statements,
                    self.enrollment,
                )
            )
            await session.commit()

        response = await client.get(
            api_app.url_path_for("statements:get_all_statements"),
        )
        assert response.status_code == 200
        assert matches(
            response.json(),
            [
                {
                    "course": {
                        "id": ...,
                        "title": self.course.title,
                        "description": self.course.description,
                        "file_link": ...,
                    },
                    "user": {
                        "id": ...,
                        "email": self.user.email,
                    },
                    "statement": {
                        "id": ...,
                        "statements": {"status": "ok"},
                    },
                }
            ],
        )

    async def test_create_statements(self, db_session, api_app, client):
        course = CMICourse(
            id=uuid4(),
            title="string",
            description="string",
            organization_id=uuid4(),
            file_link="/courses/string.zip",
        )

        user = User(id=uuid4(), email="test12@gmail.com", password="password")
        enrollment = CMIEnrollment(
            id=uuid4(),
            course_id=course.id,
            user_id=user.id,
        )

        async with db_session() as session:
            session.add_all(
                (
                    course,
                    user,
                    enrollment,
                )
            )
            await session.commit()

        response = await client.post(
            api_app.url_path_for("statements:create_statement"),
            json={
                "course_id": str(course.id),
                "user_id": str(user.id),
                "statement": {"status": "completed"},
            },
        )

        assert response.status_code == 200
        assert matches(
            response.json(),
            {
                "course": {
                    "id": ...,
                    "title": course.title,
                    "description": course.description,
                    "file_link": ...,
                },
                "user": {
                    "id": ...,
                    "email": user.email,
                },
                "statement": {
                    "id": ...,
                    "statements": {"status": "completed"},
                },
            },
        )

    async def test_create_statements__enrollment_not_found(self, api_app, client):
        response = await client.post(
            api_app.url_path_for("statements:create_statement"),
            json={
                "course_id": str(uuid4()),
                "user_id": str(uuid4()),
                "statement": {"status": "completed"},
            },
        )

        assert response.status_code == 404
