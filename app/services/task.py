import json
from pydantic import RootModel
from redis.asyncio import Redis

from app.models.task import Task
from app.core.events import event_bus
from app.services.uow import UnitOfWork
from app.schemas.task import TaskTreeResponse
from app.core.exceptions import ResourceNotFoundError
from app.events.events import TaskDeletedEvent, TaskUpdatedEvent, TaskCreatedEvent

class TaskService:
    def __init__(self, uow: UnitOfWork, redis: Redis = None):
        self.uow = uow
        self.redis = redis
        
    async def create_task(self, project_id: int, payload: dict, current_user_id: int) -> Task:
        db_data = payload.copy()
        db_data["project_id"] = project_id
        async with self.uow:
            if db_data.get("performer_id") is not None:
                is_project_member = await self.uow.projects.is_member(project_id, db_data["performer_id"])
                if not is_project_member:
                    raise ResourceNotFoundError("Исполнитель с таким ID не найден в данном проекте")
            
            if db_data.get("parent_task_id") is not None:
                is_parent_task: Task = await self.uow.tasks.is_exists_in_project(
                    db_data["parent_task_id"],
                    project_id
                )
                if not is_parent_task:
                    raise ResourceNotFoundError("Родительская задача с таким ID не найдена в данном проекте")
                
            new_task, notify_metadata = await self.uow.tasks.create_and_get_notify_metadata(db_data)
            await self.uow.commit()
            
        await event_bus.publish(
            TaskCreatedEvent(
                task_id=new_task.id,
                project_id=project_id,
                task_title=new_task.title,
                task_status=new_task.status,
                performer_id=new_task.performer_id,
                current_user_id=current_user_id,
                notify_metadata=notify_metadata
            )
        )
         
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
            serialized_data = RootModel[list[TaskTreeResponse]](tree_data).model_dump(mode="json")
            await self.redis.set(cache_key, json.dumps(serialized_data), ex=600)
            
            return tree_data
        
    async def search_project_tasks(self, project_id: int, query: str) -> list[Task] | None:
        clean_query = query.strip()
        if not clean_query:
            return []
        
        async with self.uow:
            return await self.uow.tasks.search_tasks_in_project(project_id, clean_query)
        
    async def update_task_details(self, project_id: int, task_id: int, payload: dict, current_user_id: int) -> Task:
        db_data = payload.copy()
        async with self.uow:
            if db_data.get("performer_id") is not None:
                is_project_member = await self.uow.projects.is_member(project_id, db_data["performer_id"])
                if not is_project_member:
                    raise ResourceNotFoundError("Исполнитель с таким ID не найден в данном проекте")
                
            updated_task, old_metadata, notify_metadata = await self.uow.tasks.update_and_get_all_metadata(
                task_id, project_id, db_data
            )
            if not updated_task:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")
            
            await self.uow.commit()
            
        await event_bus.publish(
            TaskUpdatedEvent(
                task_id=task_id,
                project_id=project_id,
                current_user_id=current_user_id,
                db_data=db_data,
                old_metadata=old_metadata,
                new_metadata={
                    "title": updated_task.title,
                    "status": updated_task.status,
                    "performer_id": updated_task.performer_id
                },
                notify_metadata=notify_metadata
            )
        )
        
        return updated_task
        
    async def delete_task(self, project_id: int, task_id: int, current_user_id: int):
        async with self.uow:
            is_deleted = await self.uow.tasks.delete_by_id_secure(task_id, project_id)
            if not is_deleted:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")

            await self.uow.commit()
            
        await event_bus.publish(
            TaskDeletedEvent(
                task_id,
                project_id,
                current_user_id
            )
        )
        