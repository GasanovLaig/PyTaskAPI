from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, exists, insert, select, true

from app.models.tag import Tag
from app.models.task import Task
from app.models import task_tags_table
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
    
    async def attach_tag_to_task_secure(self, project_id: int, task_id: int, tag_id: int) -> bool:
        valid_resources_query = (
            select(Task.id, Tag.id)
            .select_from(Task)
            .join(Tag, true())
            .where(
                Task.id == task_id,
                Task.project_id == project_id,
                Tag.id == tag_id,
                Tag.project_id == project_id
            )
        )
        
        query = (
            insert(task_tags_table)
            .from_select(["task_id", "tag_id"], valid_resources_query)
        )
        
        result = await self.session.execute(query)
        
        return result.rowcount > 0
    
    async def detach_tag_from_task_secure(self, project_id: int, task_id: int, tag_id: int) -> bool:
        is_task_belongs_to_project_query = select(
            exists()
            .where(
                Task.id == task_tags_table.c.task_id,
                Task.project_id == project_id
            )
        )
        
        query = (
            delete(task_tags_table)
            .where(
                task_tags_table.c.tag_id == tag_id,
                task_tags_table.c.task_id == task_id,
                is_task_belongs_to_project_query
            )
        )
        
        result = await self.session.execute(query)
        
        return result.rowcount > 0
    