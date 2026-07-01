from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.repositories.base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
        self.session = session
        
    async def create_comment(self, comment_data: dict) -> Comment:
        new_comment = Comment(**comment_data)
        self.session.add(new_comment)
        
        return new_comment
    
    async def get_comments_by_task(self, task_id: int) -> list[Comment]:
        result = await self.session.scalars(
            select(Comment)
            .where(Comment.task_id == task_id)
        )
        
        return result.all()
        
