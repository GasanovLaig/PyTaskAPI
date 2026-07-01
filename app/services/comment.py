from fastapi import HTTPException

from app.models.comment import Comment
from app.schemas.comment import CommentCreate
from app.services.uow import UnitOfWork

class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_comment(self, task_id: int, comment_data: CommentCreate):
        async with self.uow:
            task = await self.uow.tasks.get_by_id(task_id)
            if task is None:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
            
            author = await self.uow.users.get_by_id(comment_data.author_id)
            if author is None:
                raise HTTPException(status_code=404, detail="Автор с таким ID не найден")
            
            if comment_data.parent_comment_id == 0:
                comment_data.parent_comment_id = None
            
            if comment_data.parent_comment_id is not None:
                parent_comment = await self.uow.comments.get_by_id(comment_data.parent_comment_id)
                if parent_comment is None:
                    raise HTTPException(status_code=404, detail="Родительский комментарий с таким ID не найден")
                    
                if parent_comment.task_id != task_id:
                    raise HTTPException(status_code=400, detail="Родительский комментарий должен принадлежат к той же задаче что и дочерний")
                    
            data_dict = comment_data.model_dump()
            data_dict["task_id"] = task_id
            
            new_comment = await self.uow.comments.create_comment(comment_data=data_dict)
            await self.uow.commit()
            await self.uow.refresh(new_comment)
            
            return new_comment
    
    async def get_task_comments(self, project_id: int, task_id: int, user_id: int) -> list[Comment]:
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Проект с таким ID не найден")
            
            user_role = await self.uow.projects.get_user_role_in_project(project_id, user_id)
            if not user_role:
                raise HTTPException(status_code=403, detail="Вы не являетесь участником проекта")
            
            task = await self.uow.tasks.get_by_id(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
            elif task.project_id != project_id:
                raise HTTPException(status_code=400, detail="Задача должна принадлежать этому же проекту")
            
            return await self.uow.comments.get_comments_by_task(task_id)
        
    async def delete_comment_by_id(self, comment_id: int, user_id: int) -> None:
        async with self.uow:
            comment = await self.uow.comments.get_by_id(comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Комментарий с таким ID не найден")
            
            if comment.author_id != user_id:
                raise HTTPException(status_code=403, detail="Вы можете удалять только свои комментарии")
            
            await self.uow.comments.delete(comment)
            await self.uow.commit()
            
            return None
            