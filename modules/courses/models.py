import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from database.db import Base
from modules.statements.models import CMIStatement
from modules.users.models import User


class CMICourse(Base):
    __tablename__ = "cmi_courses"

    id: Column[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    title: Column[str] = Column("title", String)
    description: Column[str] = Column("description", String)
    organization_id: Column[UUID] = Column(  # FAKE FIELD
        postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    file_link: Column[str] = Column("file_link", String, nullable=True)
    deleted_at: Column[datetime.datetime] = Column(DateTime)


class CMIEnrollment(Base):
    __tablename__ = "cmi5_course_users"

    id: Column[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    course_id: Column[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("cmi_courses.id"),
        nullable=False,
    )
    user_id: Column[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    statement_id: Column[UUID] = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("cmi_statements.id"),
        nullable=True,
    )

    course: "CMICourse" = relationship("CMICourse")
    user: "User" = relationship("User")
    statement: "CMIStatement" = relationship("CMIStatement")
