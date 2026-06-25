from fastapi import HTTPException

from app.repositories.comment import CommentRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.comment import CommentCreate

class CommentService:
    def __init__(self, comment_repo: CommentRepository, task_repo: TaskRepository,
                 author_repo: UserRepository):
        self.comment_repo = comment_repo
        self.task_repo = task_repo
        self.author_repo = author_repo
        
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
                