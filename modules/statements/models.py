import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects import postgresql
from database.db import Base


class CMIStatement(Base):
    __tablename__ = "cmi_statements"

    id: Column[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    statements: Column[dict | None] = Column(postgresql.JSONB)
    deleted_at: Column[datetime.datetime] = Column(DateTime)
