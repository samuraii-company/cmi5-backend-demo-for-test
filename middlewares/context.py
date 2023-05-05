from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from database.context import ContextData, request_context


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        context_data = ContextData(
            user=None,
            db_session=request.state.db_session,
        )
        ctx_token = request_context.set(context_data)
        request.state.context = request_context
        response = await call_next(request)
        request_context.reset(ctx_token)

        return response
