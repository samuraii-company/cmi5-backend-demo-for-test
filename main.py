from fastapi import FastAPI
from fastapi.responses import JSONResponse

from middlewares import register_middlewares
from modules.courses.router import courses_router
from modules.statements.router import statement_router
from modules.users.router import users_router

app = FastAPI(title="Secure-t CMI5 Backend API", version="0.1.0")

app = register_middlewares(app)

app.include_router(users_router)
app.include_router(courses_router)
app.include_router(statement_router)


@app.post("/", response_class=JSONResponse)
async def root(data: dict) -> dict:
    """Тестовый ендпоинт, что сюда отправишь то и отдаст обратно"""

    return JSONResponse(content=data, status_code=200)
