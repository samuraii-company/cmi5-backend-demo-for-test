from uuid import UUID

import pydantic

from modules.users.schema import UserRead


class CMICoursesBase(pydantic.BaseModel):
    id: UUID
    title: str
    description: str

    class Config:
        orm_mode = True


class CMICourseRead(CMICoursesBase):
    id: UUID
    users: list[UserRead | None] = pydantic.Field(default=[])


class CMICourseCreate(pydantic.BaseModel):
    title: str
    description: str


class CMIEnrollementCreate(pydantic.BaseModel):
    course_id: UUID
    user_id: UUID


class CMIEnrollementRead(pydantic.BaseModel):
    course: CMICoursesBase
    user: UserRead

    class Config:
        orm_mode = True
