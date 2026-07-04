from fastapi import HTTPException

from app.models.comment import Comment
from app.schemas.comment import CommentCreate
from app.services.uow import UnitOfWork

class CommentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_comment(self, project_id: int, task_id: int, author_id: int, comment_data: CommentCreate):
        async with self.uow:
            task = await self.uow.tasks.get_by_id(task_id)
            if task is None or task.project_id != project_id:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена в данном проекте")

            if comment_data.parent_comment_id == 0:
                comment_data.parent_comment_id = None
            
            if comment_data.parent_comment_id is not None:
                parent_comment = await self.uow.comments.get_by_id(comment_data.parent_comment_id)
                if parent_comment is None:
                    raise HTTPException(status_code=404, detail="Родительский комментарий с таким ID не найден")
                    
                if parent_comment.task_id != task_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Родительский комментарий должен принадлежат к той же задаче что и дочерний"
                    )
                    
            data_dict = comment_data.model_dump()
            data_dict["task_id"] = task_id
            data_dict["author_id"] = author_id
            
            new_comment = await self.uow.comments.create_comment(comment_data=data_dict)
            await self.uow.commit()
            await self.uow.refresh(new_comment)
            
            return new_comment
    
    async def get_task_comments(self, project_id: int, task_id: int) -> list[Comment]:
        async with self.uow:
            task = await self.uow.tasks.get_by_id(task_id)
            if not task or task.project_id != project_id:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена в данном проекте")
            
            return await self.uow.comments.get_comments_by_task(task_id)
        
    async def delete_comment_by_id(self, project_id: int, comment_id: int, user_id: int) -> None:
        async with self.uow:
            comment = await self.uow.comments.get_by_id(comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Комментарий с таким ID не найден")
            
            task = await self.uow.tasks.get_by_id(comment.task_id)
            if not task or task.project_id != project_id:
                raise HTTPException(status_code=400, detail="Данный комментарий не принадлежит указанному проекту")
            
            if comment.author_id != user_id:
                raise HTTPException(status_code=403, detail="Вы можете удалять только свои комментарии")
            
            await self.uow.comments.delete(comment)
            await self.uow.commit()
            
            return None
            