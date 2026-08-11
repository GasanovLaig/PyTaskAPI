from fastapi import Request
from typing import AsyncGenerator

from app.services.uow import UnitOfWork

async def get_uow(request: Request) -> AsyncGenerator[UnitOfWork, None]:
    """Зависимость для роутеров FastAPI.
    Гарантирует существование одной сессии СУБД на протяжении всего HTTP-запроса.
    """
    session_factory = request.app.state.db_session_factory
    session = session_factory()
    
    try:
        yield UnitOfWork(session)
    finally:
        await session.aclose()
