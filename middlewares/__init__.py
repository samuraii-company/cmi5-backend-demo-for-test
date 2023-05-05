from fastapi import FastAPI

from .context import ContextMiddleware
from .session import SessionMiddleware


def register_middlewares(app: FastAPI) -> FastAPI:
    app.add_middleware(ContextMiddleware)
    app.add_middleware(SessionMiddleware)

    return app
