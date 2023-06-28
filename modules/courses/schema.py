from uuid import UUID

import pydantic

from modules.users.schema import UserRead
from config import settings
from shared.utils import urljoin


class CMICoursesBase(pydantic.BaseModel):
    id: UUID
    title: str
    description: str
    file_link: str | None

    @pydantic.validator("file_link")
    def validate_link(cls, v) -> str | None:
        if v and not v.startswith(urljoin("/", settings.s3_settings.bucket_name)):
            return urljoin("/", settings.s3_settings.bucket_name, v)
        return v

    class Config:
        orm_mode = True


class CMICourseRead(CMICoursesBase):
    id: UUID
    users: list[UserRead | None] = pydantic.Field(default=[])


class CMIEnrollementCreate(pydantic.BaseModel):
    course_id: UUID
    user_id: UUID


class CMIEnrollementRead(pydantic.BaseModel):
    course: CMICoursesBase
    user: UserRead

    class Config:
        orm_mode = True


class CMIUserCourseFull(pydantic.BaseModel):
    user_id: UUID
    courses: list[CMICoursesBase]
