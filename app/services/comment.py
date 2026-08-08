from app.models.comment import Comment
from app.services.uow import UnitOfWork
from app.core.exceptions import ResourceNotFoundError

class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_comment(
        self,
        project_id: int,
        task_id: int,
        current_user_id: int,
        payload: dict
    ) -> Comment:
        db_data = payload.copy()
        db_data["task_id"] = task_id
        db_data["author_id"] = current_user_id
        async with self.uow:
            is_task_exists = await self.uow.tasks.is_exists_in_project(task_id, project_id)
            if not is_task_exists:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")

            if db_data.get("parent_comment_id") is not None:
                is_parent_comment = await self.uow.comments.is_parent_comment_valid(
                    db_data["parent_comment_id"],
                    task_id
                )
                if not is_parent_comment:
                    raise ResourceNotFoundError("Родительский комментарий с таким ID не найден")
                    
            new_comment = await self.uow.comments.create(db_data)
            await self.uow.commit()
            
        return new_comment
    
    async def get_task_comments(self, project_id: int, task_id: int) -> list[Comment]:
        async with self.uow:
            return await self.uow.comments.get_comments_by_task(project_id, task_id)
        
    async def delete_comment_by_id(self, project_id: int, comment_id: int, current_user_id: int):
        async with self.uow:
            is_deleted = await self.uow.comments.delete_comment_by_id_secure(
                project_id,
                comment_id,
                current_user_id
            )
            if not is_deleted:
                raise ResourceNotFoundError("Комментарий с таким ID не найден в данном проекте")
            
            await self.uow.commit()
            