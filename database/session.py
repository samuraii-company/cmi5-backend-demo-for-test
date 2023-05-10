import functools
from asyncio import current_task
from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker

from database.context import ContextData, get_context

from .db import DBSession, engine


async def _get_session():
    Session = async_scoped_session(
        sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False),
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


async def get_session(
    context: ContextData = Depends(get_context),
) -> DBSession:
    return context.db_session


def provide_session(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with SessionManager() as session:
            return await func(*args, session, **kwargs)

    return wrapper
