from fastapi import FastAPI
from fastapi.responses import JSONResponse

from middlewares import register_middlewares
from modules.courses.router import courses_router
from modules.statements.router import statement_router
from modules.users.router import users_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Secure-t CMI5 Backend API", version="0.1.0")

app = register_middlewares(app)

app.include_router(users_router)
app.include_router(courses_router)
app.include_router(statement_router)


@app.post("/", response_class=JSONResponse)
async def root() -> JSONResponse:
    """Тестовый ендпоинт"""

    return JSONResponse(content={"ok": True}, status_code=200)
