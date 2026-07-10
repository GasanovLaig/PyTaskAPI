from fastapi import HTTPException, status

from app.models.comment import Comment
from app.models.project_member import Role
from app.schemas.comment import CommentCreate
from app.services.uow import UnitOfWork

class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_comment(
        self,
        project_id: int,
        task_id: int,
        current_user_id: int,
        comment_data: CommentCreate
    ) -> Comment:
        async with self.uow:
            is_task_exists = await self.uow.tasks.is_exists_in_project(task_id, project_id)
            if not is_task_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Задача с таким ID не найдена в данном проекте"
                )

            if comment_data.parent_comment_id == 0:
                comment_data.parent_comment_id = None
            
            if comment_data.parent_comment_id is not None:
                is_parent_comment = await self.uow.comments.is_parent_comment_valid(
                    comment_data.parent_comment_id,
                    task_id
                )
                if not is_parent_comment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Родительский комментарий с таким ID не найден"
                    )
                    
            data_dict = comment_data.model_dump()
            data_dict["task_id"] = task_id
            data_dict["author_id"] = current_user_id
            
            new_comment = await self.uow.comments.create_comment(comment_data=data_dict)
            await self.uow.commit()
            await self.uow.refresh(new_comment)
            
            return new_comment
    
    async def get_task_comments(self, project_id: int, task_id: int) -> list[Comment]:
        async with self.uow:
            is_task_exists = await self.uow.tasks.is_exists_in_project(task_id, project_id)
            if not is_task_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Задача с таким ID не найдена в данном проекте"
                )
            
            return await self.uow.comments.get_comments_by_task(task_id)
        
    async def delete_comment_by_id(self, project_id: int, comment_id: int, current_user_id: int):
        async with self.uow:
            metadata = await self.uow.comments.get_comment_metadata(comment_id)
            if not metadata:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Комментарий с таким ID не найден"
                )
            
            author_id, real_project_id = metadata
            if real_project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Комментарий с таким ID не найден в данном проекте"
                )
            
            is_author = author_id == current_user_id
            user_role = await self.uow.projects.get_user_role_in_project(
                project_id,
                current_user_id
            )
            is_moderator = user_role in [Role.OWNER, Role.MANAGER]
            if not (is_author or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="У вас нет прав на удаление этого комментария"
                )
            
            await self.uow.comments.delete_by_id(comment_id)
            await self.uow.commit()
            