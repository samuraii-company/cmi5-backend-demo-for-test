from fastapi import FastAPI

from middlewares import register_middlewares
from modules.courses.router import courses_router
from modules.statements.router import statement_router
from modules.users.router import users_router
import logging
from app import __version__


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app: FastAPI = FastAPI(
        title="CMI5 Backend API",
        version=__version__,
    )

    app.include_router(users_router)
    app.include_router(courses_router)
    app.include_router(statement_router)
    app = register_middlewares(app)

    return app


app = create_app()
