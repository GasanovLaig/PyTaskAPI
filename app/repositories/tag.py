from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.base import BaseRepository

class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Tag, session=session)
        self.session = session
        
    async def get_by_name(self, name: str) -> Tag | None:
        result = await self.session.execute(select(Tag).where(Tag.name == name))
        
        return result.scalar_one_or_none()
    