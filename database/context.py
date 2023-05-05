from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from modules.users.models import User
    from .db import DBSession


@dataclass(frozen=True)
class ContextData:
    db_session: Optional["DBSession"]


request_context: ContextVar[ContextData | None] = ContextVar("context", default=None)


def get_context() -> ContextData:
    context_data = request_context.get()
    if not context_data:
        raise ValueError

    return context_data
