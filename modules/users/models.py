import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects import postgresql

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Column[UUID] = Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    email: Column[str] = Column("email", String)
    password: Column[str] = Column("password", postgresql.VARCHAR, default="")
    deleted_at: Column[datetime.datetime] = Column(DateTime)
