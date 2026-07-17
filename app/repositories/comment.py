from sqlalchemy import delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.project_member import ProjectMember, Role
from app.models.task import Task
from app.repositories.base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Comment, session)
        
    async def get_comments_by_task(self, project_id: int, task_id: int) -> list[Comment]:
        result = await self.session.scalars(
            select(Comment)
            .join(Task, Comment.task_id == Task.id)
            .where(
                Comment.task_id == task_id,
                Task.project_id == project_id
            )
        )
        
        return result.all()
    
    async def is_parent_comment_valid(self, parent_comment_id: int, expected_task_id: int) -> bool:
        return await self.session.scalar(select(exists().where(
            Comment.id == parent_comment_id,
            Comment.task_id == expected_task_id
        )))
    
    async def delete_comment_by_id_secure(self, project_id: int, comment_id: int, user_id: int) -> None:
        is_comment_in_project = select(
            exists()
            .where(
                Task.id == Comment.task_id,
                Task.project_id == project_id
            )
        )
        
        is_user_moderator = select(
            exists()
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                ProjectMember.role.in_([Role.OWNER, Role.MANAGER])
            )
        )
        
        result = await self.session.execute(
            delete(Comment)
            .where(
                Comment.id == comment_id,
                is_comment_in_project,
                or_(
                    Comment.author_id == user_id,
                    is_user_moderator
                )
            )
        )
        
        return result.rowcount > 0
        