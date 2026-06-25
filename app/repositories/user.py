from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)
        
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.scalars(select(User).where(User.email == email))
        
        return result.one_or_none()
