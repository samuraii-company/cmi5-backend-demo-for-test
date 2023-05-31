import asyncio

import faker.config
import pytest

import random
import string
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
import os
import secrets
from asyncio import current_task
from contextlib import asynccontextmanager
import functools
from sqlalchemy import MetaData, Table
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool
from sqlalchemy.util import FacadeDict

from database import session
from config import settings
from database.db import json_serializer
from shared.sqlalchemy import (
    create_database,
    drop_database,
    list_databases,
)

postgres_settings = settings.postgres_settings

faker.config.DEFAULT_LOCALE = "ru_RU"

EXCLUDED_TABLES_PREFIXES = []

FORCE_INCLUDE = [
    "cmi_courses",
    "cmi5_course_users",
    "cmi_statements",
    "users",
]


@pytest.fixture(scope="session")
def api_app(db_session):
    """FastAPI app fixture."""
    from fastapi import FastAPI

    from middlewares import register_middlewares

    from modules.courses.router import courses_router
    from modules.statements.router import statement_router
    from modules.users.router import users_router
    from app import __version__

    def create_app() -> FastAPI:
        app: FastAPI = FastAPI(title="Secure-t CMI5 Backend API", version=__version__)

        app.include_router(courses_router)
        app.include_router(statement_router)
        app.include_router(users_router)
        app = register_middlewares(app)

        return app

    return create_app()


@pytest.fixture(scope="session")
async def client(api_app):
    """Async http client for FastAPI application, ASGI init signals handled by
    LifespanManager.
    """
    async with LifespanManager(api_app, startup_timeout=100, shutdown_timeout=100):
        base_chars = "".join(random.choices(string.ascii_uppercase, k=4))
        async with AsyncClient(app=api_app, base_url=f"http://{base_chars}") as ac:
            yield ac


def pytest_addoption(parser):
    parser.addoption(
        "--keepdb",
        action="store_true",
        help="Don't drop the test database at the end of tests",
    )
    parser.addoption(
        "--flushdb",
        action="store_true",
        help="Delete all previous test databases",
    )


@pytest.fixture(scope="session")
def event_loop():
    """Singe loop for whole test suite.
    If not overridden, the loop will crash with an invalid session scope error
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def POSTGRES_TEST_DSN():
    if os.getenv("TEST_DB"):
        POSTGRES_TEST_DSN = os.getenv("TEST_DB")
    else:
        db_name = f"{postgres_settings.name}_test_{secrets.token_hex(4).lower()}"
        POSTGRES_TEST_DSN = f"{postgres_settings.get_dsn(db_name)}"
    yield POSTGRES_TEST_DSN


@pytest.fixture(scope="session")
async def test_engine(POSTGRES_TEST_DSN):
    engine: AsyncEngine = create_async_engine(
        POSTGRES_TEST_DSN,
        echo=False,
        poolclass=AsyncAdaptedQueuePool,
        json_serializer=json_serializer,
    )
    yield engine
    await engine.dispose()


async def flush_databases(POSTGRES_TEST_DSN, db_list):
    print("Flusing databases:")
    for database in db_list:
        print(database)
        await drop_database(POSTGRES_TEST_DSN, database)


@pytest.fixture(scope="session")
async def create_test_db(POSTGRES_TEST_DSN, test_engine, request, load_models):
    db_list = await list_databases(POSTGRES_TEST_DSN)

    if request.config.getoption("--flushdb"):
        await flush_databases(POSTGRES_TEST_DSN, db_list)

    if len(db_list) > 0 and not os.getenv("DRONE_PIPELINE"):
        print(f"Found existing test databases! {','.join(db_list)}")
        inp: str = input("Clean databases? [yes/no] \n")
        if inp.startswith("y"):
            await flush_databases(POSTGRES_TEST_DSN, db_list)

    elif len(db_list) > 0 and os.getenv("DRONE_PIPELINE"):
        await flush_databases(POSTGRES_TEST_DSN, db_list)

    await create_database(POSTGRES_TEST_DSN)

    from database.db import Base

    meta = Base.metadata
    load_models()
    meta.tables = await filter_broken_tables(meta)
    pytest.reversed_tables = list(reversed(meta.sorted_tables))

    async with test_engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    yield 1

    if not request.config.getoption("--keepdb"):
        await drop_database(POSTGRES_TEST_DSN)


async def filter_broken_tables(meta: MetaData) -> FacadeDict[str, Table]:
    filtered_tables = FacadeDict()
    for table_name, table in meta.tables.items():
        if table_name in FORCE_INCLUDE:
            filtered_tables._insert_item(table_name, table)
            continue

        excluded_by_prefix = any(
            table_name.startswith(prefix) for prefix in EXCLUDED_TABLES_PREFIXES
        )
        if not excluded_by_prefix:
            filtered_tables._insert_item(table_name, table)

    return filtered_tables


@pytest.fixture(autouse=True)
async def truncate_db(db_session):
    yield
    tables = ",".join(x.name for x in pytest.reversed_tables)
    text = f"TRUNCATE {tables} RESTART IDENTITY;"

    async with db_session() as conn:
        await conn.execute(text)


@pytest.fixture(scope="session")
async def db_session(
    create_test_db,
    test_engine,
):
    async def _get_session():
        Session = async_scoped_session(
            sessionmaker(
                bind=test_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            ),
            scopefunc=current_task,
        )
        session = Session()

        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        else:
            await session.commit()
        finally:
            await session.close()

    SessionManager = asynccontextmanager(_get_session)

    def provide_session(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with SessionManager() as session:
                return await func(*args, session, **kwargs)

        return wrapper

    session.SessionManager = SessionManager
    session.provide_session = provide_session

    return asynccontextmanager(_get_session)


@pytest.fixture(scope="session")
def load_models():
    def init_func():
        from modules.courses.models import CMICourse, CMIEnrollment  # noqa
        from modules.statements.models import CMIStatement  # noqa
        from modules.users.models import User  # noqa

    return init_func
