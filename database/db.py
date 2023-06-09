import json
from typing import Any, NewType
from uuid import UUID

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool
from config import settings

DBSession = NewType("DBSession", AsyncSession)
database = settings.postgres_settings


def json_serializer(obj: Any) -> str:
    class UUIDSerializer(json.JSONEncoder):
        def default(self, o: Any) -> str:
            if isinstance(o, UUID):
                return str(o)
            return super().default(o)

    return json.dumps(obj, cls=UUIDSerializer)


DATABASE_URL = f"postgresql+asyncpg://{database.username}:{database.password}@{database.host}:{database.port}/{database.name}"

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=AsyncAdaptedQueuePool,
    json_serializer=json_serializer,
)

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base = declarative_base(metadata=MetaData(naming_convention=convention))
