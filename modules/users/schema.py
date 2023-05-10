from uuid import UUID

import pydantic


class UserRead(pydantic.BaseModel):
    id: UUID
    email: str

    class Config:
        orm_mode = True


class UserCreate(pydantic.BaseModel):
    email: str
    password: str
