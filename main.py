from fastapi import FastAPI
from fastapi.responses import JSONResponse
from middlewares import register_middlewares

from modules.users.router import users_router

app = FastAPI(title="CMI5 Backend API", version="0.1.0")

app = register_middlewares(app)

app.include_router(users_router)
# app.include_router(users_router.router)
# app.include_router(posts_router.router)
# app.include_router(comments_router.router)
# app.include_router(likes_router.router)


@app.post("/", response_class=JSONResponse)
async def root(data: dict) -> dict:
    """Тестовый ендпоинт, что сюда отправишь то и отдаст обратно"""

    return JSONResponse(content=data, status_code=200)
