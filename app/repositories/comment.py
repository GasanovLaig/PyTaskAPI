from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.task import Task
from app.repositories.base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
        self.session = session
        
    async def get_comments_by_task(self, task_id: int) -> list[Comment]:
        result = await self.session.scalars(
            select(Comment)
            .where(Comment.task_id == task_id)
        )
        
        return result.all()
    
    async def is_parent_comment_valid(self, parent_comment_id: int, expected_task_id: int) -> bool:
        query = select(exists().where(
            Comment.id == parent_comment_id,
            Comment.task_id == expected_task_id
        ))
        
        return await self.session.scalar(query)
    
    async def get_comment_metadata(self, comment_id: int) -> tuple[int, int] | None:
        query = (
            select(Comment.author_id, Task.project_id)
            .join(Task, Comment.task_id == Task.id)
            .where(Comment.id == comment_id)
        )
        result = await self.session.execute(query)
        
        return result.fetchone()
        