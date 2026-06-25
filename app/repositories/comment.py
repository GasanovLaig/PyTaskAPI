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
        await self.session.commit()
        await self.session.refresh(new_comment)
        
        return new_comment
