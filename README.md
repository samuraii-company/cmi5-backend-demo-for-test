Демо стенд для базовой работы с курсами, юзерами и их состояниями

Запуск
```
docker compose up -d --build
```

Дока
```
http://0.0.0.0:5000/docs
```

Структура моделей
```
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
```

```
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
deleted_at: Column[datetime.datetime] = Column(DateTime)
```

```
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
```
```
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
```
