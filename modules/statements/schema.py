from uuid import UUID

import pydantic

from modules.courses.schema import CMICoursesBase
from modules.users.schema import UserRead


class CMIStatementsCreate(pydantic.BaseModel):
    user_id: UUID
    course_id: UUID
    statement: dict


class CMIStatementBase(pydantic.BaseModel):
    id: UUID
    statements: dict

    class Config:
        orm_mode = True


class CMIStatementRead(pydantic.BaseModel):
    course: CMICoursesBase
    user: UserRead
    statement: CMIStatementBase

    class Config:
        orm_mode = True
