import json
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

from app.core.exceptions import ResourceNotFoundError
from app.services.uow import UnitOfWork
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, uow: UnitOfWork, redis: Redis = None):
        self.uow = uow
        self.redis = redis
        
    async def create_task(self, project_id: int, task_data: TaskCreate) -> Task:
        async with self.uow:
            if task_data.performer_id is not None:
                is_project_member = await self.uow.projects.is_member(project_id, task_data.performer_id)
                if not is_project_member:
                    raise ResourceNotFoundError("Исполнитель с таким ID не найден в данном проекте")
            
            if task_data.parent_task_id == 0:
                task_data.parent_task_id = None
                
            if task_data.parent_task_id is not None:
                is_parent_task: Task = await self.uow.tasks.is_exists_in_project(
                    task_data.parent_task_id,
                    project_id
                )
                if not is_parent_task:
                    raise ResourceNotFoundError("Родительская задача с таким ID не найдена в данном проекте")
                
            db_data = task_data.model_dump()
            db_data["project_id"] = project_id
            new_task = await self.uow.tasks.create(db_data)
            await self.uow.commit()
            
            cache_key = f"project:{project_id}:tasks_tree"
            await self.redis.delete(cache_key)
            
            return new_task
        
    async def get_task_by_id(self, project_id: int, task_id: int) -> Task:
        async with self.uow:
            task = await self.uow.tasks.get_task_with_tags_secure(project_id, task_id)
            if not task:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")
            
            return task
    
    async def get_project_tasks(self, project_id: int) -> list[Task]:
        async with self.uow:
            return await self.uow.tasks.get_tasks_by_project(project_id)
    
    async def get_project_tasks_tree(self, project_id: int) -> list[Task]:
        cache_key = f"project:{project_id}:tasks_tree"
        cached_tree = await self.redis.get(cache_key)
        if cached_tree:
            return json.loads(cached_tree)
        
        async with self.uow:
            tree_data = await self.uow.tasks.get_project_tasks_tree(project_id)
            serialized_data = jsonable_encoder(tree_data)
            
            await self.redis.set(cache_key, json.dumps(serialized_data), ex=600)
            
            return tree_data
        
    async def update_task_details(self, project_id: int, task_id: int, task_data: TaskUpdate) -> Task:
        async with self.uow:
            if task_data.performer_id is not None:
                is_project_member = await self.uow.projects.is_member(project_id, task_data.performer_id)
                if not is_project_member:
                    raise ResourceNotFoundError("Исполнитель с таким ID не найден в данном проекте")
            
            db_data = task_data.model_dump(exclude_unset=True)
            updated_task = await self.uow.tasks.update_by_id_secure(task_id, project_id, db_data)
            if not updated_task:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")
                
            await self.uow.commit()
            cache_key = f"project:{project_id}:tasks_tree"
            await self.redis.delete(cache_key)
            
            return updated_task
        
    async def delete_task(self, project_id: int, task_id: int):
        async with self.uow:
            is_deleted = await self.uow.tasks.delete_by_id_secure(task_id, project_id)
            if not is_deleted:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")
            
            await self.uow.commit()
        
        await self.redis.delete(f"project:{project_id}:tasks_tree")
        