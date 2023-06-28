from dataclasses import dataclass
import datetime
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import and_, select, update
from sqlalchemy.orm import selectinload

from database.db import DBSession
from database.session import get_session
from modules.courses.models import CMIEnrollment
from modules.users.models import User

from .models import CMICourse


@dataclass
class CourseDTO:
    title: str
    description: str
    file_path: str


class CMICourseService:
    model: CMICourse = CMICourse

    def __init__(
        self,
        session: DBSession = Depends(get_session),
    ):
        self.session = session

    async def get_by_id(self, course_id: UUID) -> CMICourse | None:
        """Get course by id

        Args:
            course_id (UUID): course id

        Returns:
            CMICourse | None: course instance or none
        """
        course = (
            await self.session.execute(
                select(self.model).where(
                    and_(
                        self.model.id == course_id,
                        self.model.deleted_at.is_(None),
                    )
                )
            )
        ).scalar()

        return course

    async def get_by_user_id(self, user_id: UUID) -> list[CMICourse | None]:
        """Get course by user id

        Args:
            user_id (UUID): user id

        Returns:
            list[CMICourse | None]: list courses or empty list
        """
        courses = (
            (
                await self.session.execute(
                    select(self.model)
                    .join(CMIEnrollment, self.model.id == CMIEnrollment.course_id)
                    .where(
                        CMIEnrollment.user_id == user_id,
                        self.model.deleted_at.is_(None),
                    )
                )
            )
            .scalars()
            .all()
        )

        return courses

    async def create(self, data: CourseDTO) -> CMICourse:
        """Create a CMI5 Course

        Args:
            data (dict): data about course

        Returns:
            CMICourse: CMI5Course object
        """

        course = CMICourse(
            id=uuid4(),
            title=data.title,
            description=data.description,
            organization_id="ebbc58b4db644e93bdfbe493534e847c",
            file_link=data.file_path,
        )  # fake organization id

        self.session.add(course)
        await self.session.commit()

        return course

    async def delete(self, course: CMICourse) -> None:
        """
        Delete CMI5 Course and all CMIEnrollment rows by this course

        Args:
            course (CMICourse): CMI5Course object

        Returns:
            None:
        """

        await self.session.execute(
            update(CMIEnrollment)
            .where(CMIEnrollment.course_id == course.id)
            .values(deleted_at=datetime.datetime.utcnow())
        )

        await self.session.execute(
            update(self.model)
            .where(self.model.id == course.id)
            .values(deleted_at=datetime.datetime.utcnow())
        )

    async def get_users(self, course: CMICourse) -> list[User | None]:
        """Get users by CMI5Course

        Args:
            course (CMICourse): course object

        Returns:
            list[User | None]: list with users or empty list
        """

        users = (
            (
                await self.session.execute(
                    select(User)
                    .join(CMIEnrollment, User.id == CMIEnrollment.user_id)
                    .where(
                        and_(
                            CMIEnrollment.course_id == course.id,
                            User.deleted_at.is_(None),
                        )
                    )
                )
            )
            .scalars()
            .all()
        )

        return users

    async def get_enrollment(
        self, course_id: UUID, user_id: UUID
    ) -> CMIEnrollment | None:
        """Get data about CMICourse assigned on user or not

        Args:
            course_id (CMICourse): CMI5Course id
            user_id (User): User id

        Returns:
            CMIEnrollment | None: CMIEnrollment or None
        """

        enrollment = (
            await self.session.execute(
                select(CMIEnrollment)
                .where(
                    and_(
                        CMIEnrollment.course_id == course_id,
                        CMIEnrollment.user_id == user_id,
                    )
                )
                .options(selectinload(CMIEnrollment.statement))
                .options(selectinload(CMIEnrollment.user))
                .options(selectinload(CMIEnrollment.course))
            )
        ).scalar()
        return enrollment

    async def set_enrollment(self, course: CMICourse, user: User) -> CMIEnrollment:
        """Set course on user

        Args:
            course (CMICourse): CMI5 Course
            user (User): User

        Returns:
            CMIEnrollment: CMI5 nrollment
        """

        enrollment = CMIEnrollment(
            id=uuid4(),
            course_id=course.id,
            user_id=user.id,
        )
        self.session.add(enrollment)
        await self.session.commit()

        return await self._get_enrollment_by_id(enrollment.id)

    async def get_all(self) -> list[CMICourse | None]:
        """Get all not deleted courses"""

        courses = (
            (
                await self.session.execute(
                    select(self.model).where(self.model.deleted_at.is_(None))
                )
            )
            .scalars()
            .all()
        )

        return courses

    async def _get_enrollment_by_id(self, enrollment_id: UUID) -> CMIEnrollment | None:
        """Get enrollment by id

        Args:
            enrollment_id (UUID): enrollment id

        Returns:
            CMIEnrollment | None: enrollemnt instance or none
        """
        return (
            await self.session.execute(
                select(CMIEnrollment)
                .where(CMIEnrollment.id == enrollment_id)
                .options(selectinload(CMIEnrollment.user))
                .options(selectinload(CMIEnrollment.course))
            )
        ).scalar()
