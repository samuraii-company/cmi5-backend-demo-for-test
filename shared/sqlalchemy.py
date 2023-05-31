import sqlalchemy as sa
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

POSTGRES_DB = "postgres"


async def list_databases(url):
    """Issue the appropriate DROP DATABASE statement.

    :param url: A SQLAlchemy engine URL.

    Works similar to the :ref:`create_database` method in that both url text
    and a constructed url are accepted. ::

        drop_database('postgresql://postgres@localhost/name')
        drop_database(engine.url)

    """

    url = make_url(url)
    url = url.set(database=POSTGRES_DB)
    engine = create_async_engine(url)

    async with engine.connect() as connection:
        result = await connection.execute(
            sa.text(
                """
            SELECT datname FROM pg_database where datname like '%_test_%';
            """
            )
        )
    await engine.dispose()
    return result.scalars().all()


async def create_database(url, encoding="utf8", template=None):
    """Issue the appropriate CREATE DATABASE statement.

    :param url: A SQLAlchemy engine URL.
    :param encoding: The encoding to create the database as.
    :param template:
        The name of the template from which to create the new database. At the
        moment only supported by PostgreSQL driver.

    To create a database, you can pass a simple URL that would have
    been passed to ``create_engine``. ::

        create_database('postgresql://postgres@localhost/name')

    You may also pass the url from an existing engine. ::

        create_database(engine.url)

    Has full support for mysql, postgres, and sqlite. In theory,
    other database engines should be supported.
    """

    url = make_url(url)
    database = url.database
    url = url.set(database=POSTGRES_DB)

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    text = sa.text("CREATE DATABASE {0} ENCODING '{1}'".format(database, encoding))

    async with engine.begin() as connection:
        await connection.execute(text)

    await engine.dispose()


async def drop_database(url, db_name=None):
    """Issue the appropriate DROP DATABASE statement.

    :param url: A SQLAlchemy engine URL.

    Works similar to the :ref:`create_database` method in that both url text
    and a constructed url are accepted. ::

        drop_database('postgresql://postgres@localhost/name')
        drop_database(engine.url)

    """

    url = make_url(url)
    if not db_name:
        db_name = url.database

    url = url.set(database=POSTGRES_DB)

    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as connection:
        # Disconnect all users from the database we are dropping.
        version = connection.dialect.server_version_info
        pid_column = "pid" if (version >= (9, 2)) else "procpid"
        text = """
        SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '%(database)s'
        AND %(pid_column)s <> pg_backend_pid();
        """ % {
            "pid_column": pid_column,
            "database": db_name,
        }
        await connection.execute(sa.text(text))

        # Drop the database.
        text = "DROP DATABASE {0}".format(db_name)
        await connection.execute(sa.text(text))

    await engine.dispose()


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
