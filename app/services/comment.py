from fastapi import HTTPException

from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.comment import CommentCreate

class CommentService:
    def __init__(self, comment_repo: CommentRepository, task_repo: TaskRepository,
                 author_repo: UserRepository, project_repo: ProjectRepository = None):
        self.comment_repo = comment_repo
        self.task_repo = task_repo
        self.author_repo = author_repo
        self.project_repo = project_repo
        
    async def create_new_comment(self, task_id: int, comment_data: CommentCreate):
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
        
        author = await self.author_repo.get_by_id(comment_data.author_id)
        if author is None:
            raise HTTPException(status_code=404, detail="Автор с таким ID не найден")
        
        if comment_data.parent_comment_id == 0:
            comment_data.parent_comment_id = None
        
        if comment_data.parent_comment_id is not None:
            parent_comment = await self.comment_repo.get_by_id(comment_data.parent_comment_id)
            if parent_comment is None:
                raise HTTPException(status_code=404, detail="Родительский комментарий с таким ID не найден")
                
            if parent_comment.task_id != task_id:
                raise HTTPException(status_code=400, detail="Родительский комментарий должен принадлежат к той же задаче что и дочерний")
                
        data_dict = comment_data.model_dump()
        data_dict["task_id"] = task_id
        
        return await self.comment_repo.create_comment(comment_data=data_dict)
    
    async def get_task_comments(self, project_id: int, task_id: int, user_id: int) -> list[Comment]:
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.project_id != project_id:
            raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
        
        user_role = await self.project_repo.get_user_role_in_project(project_id, user_id)
        if not user_role:
            raise HTTPException(status_code=403, detail="Вы не являетесь участником проекта")
        
        return await self.comment_repo.get_comments_by_task(task_id)
        
    async def delete_comment_by_id(self, comment_id: int, user_id: int) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Комментарий с таким ID не найден")
        
        if comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Вы можете удалять только свои комментарии")
        
        await self.comment_repo.delete(comment)
        
        return None 
                