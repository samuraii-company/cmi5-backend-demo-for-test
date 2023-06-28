from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .context import ContextMiddleware
from .session import SessionMiddleware


def register_middlewares(app: FastAPI) -> FastAPI:
    app.add_middleware(ContextMiddleware)
    app.add_middleware(SessionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
