from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.base import BaseRepository

class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Tag, session=session)
        
    async def get_all_tags_by_project(self, project_id: int) -> list[Tag] | None:
        result = await self.session.scalars(
            select(Tag)
            .where(Tag.project_id == project_id)
        )
        
        return result.all()
    