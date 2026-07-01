from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.uow import UnitOfWork

async def get_uow(session: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(session)
