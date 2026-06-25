from fastapi import HTTPException

from app.models.task import Task
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.task import TaskCreate, TaskCreate

class TaskService:
    def __init__(self, task_repo: TaskRepository, project_repo: ProjectRepository, user_repo: UserRepository):
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.user_repo = user_repo
        
    async def create_task(self, project_id: int, task_data: TaskCreate) -> Task:
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Проекта с таким ID не найден")
        
        if task_data.performer_id is not None:
            performer = await self.user_repo.get_by_id(task_data.performer_id)
            if performer is None:
                raise HTTPException(status_code=404, detail="Испольнитель с таким ID не найден")
        
        if task_data.parent_task_id == 0:
            task_data.parent_task_id = None
            
        if task_data.parent_task_id is not None:
            parent_task: Task = await self.task_repo.get_by_id(task_data.parent_task_id)
            if parent_task is None:
                raise HTTPException(status_code=404, detail="Родительская задача с таким ID не найдена")
            
            if parent_task.project_id != project_id:
                raise HTTPException(status_code=400, detail="Родительская задача должна быть из того же проекта, что и создаваемая задача")
            
        task_dict = task_data.model_dump()
        task_dict["project_id"] = project_id
        
        return await self.task_repo.create_task(task_data=task_dict)
        