from fastapi import HTTPException

from app.services.uow import UnitOfWork
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_task(self, project_id: int, task_data: TaskCreate) -> Task:
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if project is None:
                raise HTTPException(status_code=404, detail="Проекта с таким ID не найден")
            
            if task_data.performer_id is not None:
                performer = await self.uow.users.get_by_id(task_data.performer_id)
                if performer is None:
                    raise HTTPException(status_code=404, detail="Испольнитель с таким ID не найден")
            
            if task_data.parent_task_id == 0:
                task_data.parent_task_id = None
                
            if task_data.parent_task_id is not None:
                parent_task: Task = await self.uow.tasks.get_by_id(task_data.parent_task_id)
                if parent_task is None:
                    raise HTTPException(status_code=404, detail="Родительская задача с таким ID не найдена")
                
                if parent_task.project_id != project_id:
                    raise HTTPException(status_code=400, detail="Родительская задача должна быть из того же проекта, что и создаваемая задача")
                
            task_dict = task_data.model_dump()
            task_dict["project_id"] = project_id
            
            task = await self.uow.tasks.create_task(task_data=task_dict)
        
            await self.uow.commit()
            
            return task
        
    async def get_task_by_id(self, task_id: int) -> Task:
        async with self.uow:
            task = await self.uow.tasks.get_with_tags(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
            
            return task
    
    async def delete_task(self, task_id: int):
        async with self.uow:
            task = await self.uow.tasks.get_by_id(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
            
            await self.uow.tasks.delete(task)
            
            return {"detail": "Задача успешно удалена"}
    
    async def get_project_tasks(self, project_id:int, user_id: int) -> list[Task]:
        async with self.uow:
            user_role = await self.uow.projects.get_user_role_in_project(project_id, user_id)
            if not user_role:
                raise HTTPException(status_code=403, detail="Вы не являетесь участником этого проекта")
            
            return await self.uow.tasks.get_tasks_by_project(project_id)
    
    async def update_task_details(self, project_id: int, task_id: int, user_id: int, task_data: TaskUpdate) -> Task:
        async with self.uow:
            user_role = await self.uow.projects.get_user_role_in_project(project_id, user_id)
            if not user_role:
                raise HTTPException(status_code=403, detail="Вы не являетесь участником этого проекта")
            
            task = await self.uow.tasks.get_with_tags(task_id)
            if not task or task.project_id != project_id:
                raise HTTPException(status_code=404, detail="Задача не найдена в данном проекте")
            
            if task_data.performer_id is not None:
                performer = await self.uow.users.get_by_id(task_data.performer_id)
                if not performer:
                    raise HTTPException(status_code=404, detail="Указанный исполнитель не найден")
                
            update_dict = task_data.model_dump(exclude_unset=True)
            updated_task = await self.uow.tasks.update(task, update_dict)
            await self.uow.commit()
            
            return updated_task
    
    async def get_project_tasks_tree(self, project_id: int, user_id: int) -> list[Task]:
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Проект с таким ID не найден")
            
            user_role = await self.uow.projects.get_user_role_in_project(project_id, user_id)
            if not user_role:
                raise HTTPException(status_code=403, detail="Вы не являетесь участником этого проекта")
            
            return await self.uow.tasks.get_project_task_tree(project_id)
        