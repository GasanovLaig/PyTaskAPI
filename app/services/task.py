import json
from arq import ArqRedis
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder

from app.models.task import Task
from app.services.uow import UnitOfWork
from app.utils.enqueue_task import enqueue_task
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.exceptions import ResourceNotFoundError
from app.utils.clear_cache_key import clear_cache_key

class TaskService:
    def __init__(self, uow: UnitOfWork, redis: Redis = None, arq_pool: ArqRedis = None):
        self.uow = uow
        self.redis = redis
        self.arq_pool = arq_pool
        
    async def create_task(self, project_id: int, task_data: TaskCreate, current_user_id: int) -> Task:
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
            
            await enqueue_task(
                self.arq_pool,
                "log_activity_task",
                user_id=current_user_id,
                project_id=project_id,
                action="task.created",
                resource_type="Task",
                resource_id=new_task.id,
                details={
                    "task_title": new_task.title,
                    "status": new_task.status
                }
            )
            
            await clear_cache_key(self.redis, f"project:{project_id}:tasks_tree")
            
            if new_task.performer_id is not None:
                performer_email, project_title = await self.uow.tasks.get_metadata_for_celery(
                    project_id,
                    new_task.performer_id
                )
                await enqueue_task(
                    self.arq_pool,
                    "send_assignee_email_task",
                    performer_email=performer_email,
                    task_title=new_task.title,
                    project_title=project_title
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
            serialized_data = jsonable_encoder(tree_data)
            
            await self.redis.set(cache_key, json.dumps(serialized_data), ex=600)
            
            return tree_data
        
    async def search_project_tasks(self, project_id: int, query: str) -> list[Task] | None:
        clean_query = query.strip()
        if not clean_query:
            return []
        
        async with self.uow:
            return await self.uow.tasks.search_tasks_in_project(project_id, clean_query)
        
    async def update_task_details(self, project_id: int, task_id: int, task_data: TaskUpdate, current_user_id: int) -> Task:
        async with self.uow:
            if task_data.performer_id is not None:
                is_project_member = await self.uow.projects.is_member(project_id, task_data.performer_id)
                if not is_project_member:
                    raise ResourceNotFoundError("Исполнитель с таким ID не найден в данном проекте")
            
            old_task_title, old_task_status, old_task_performer_id = await self.uow.tasks.get_task_log_metadata_secure(
                project_id,
                task_id
            )
            
            db_data = task_data.model_dump(exclude_unset=True)
            updated_task = await self.uow.tasks.update_by_id_secure(task_id, project_id, db_data)
            if not updated_task:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")

            history_details = {}
            if "title" in db_data and updated_task.title != old_task_title:
                history_details["old_title"] = old_task_title
                history_details["new_title"] = updated_task.title
            if "status" in db_data and updated_task.status != old_task_status:
                history_details["old_status"] = old_task_status
                history_details["new_status"] = updated_task.status
            if "performer_id" in db_data and updated_task.performer_id != old_task_performer_id:
                history_details["old_performer_id"] = old_task_performer_id
                history_details["new_performer_id"] = updated_task.performer_id
            
            await enqueue_task(
                self.arq_pool,
                "log_activity_task",
                user_id=current_user_id,
                project_id=project_id,
                action="task.updated",
                resource_type="Task",
                resource_id=task_id,
                details=history_details
            )
            
            await self.uow.commit()
            await clear_cache_key(self.redis, f"project:{project_id}:tasks_tree")
            
            if ("performer_id" in task_data
                and updated_task.performer_id != old_task_performer_id
                and updated_task.performer_id is not None):
                performer_email, project_title = await self.uow.tasks.get_metadata_for_celery(
                    project_id,
                    updated_task.performer_id
                )
                await enqueue_task(
                    self.arq_pool,
                    "send_assignee_email_task",
                    performer_email=performer_email,
                    task_title=updated_task.title,
                    project_title=project_title
                )
            
            return updated_task
        
    async def delete_task(self, project_id: int, task_id: int, current_user_id: int):
        async with self.uow:
            is_deleted = await self.uow.tasks.delete_by_id_secure(task_id, project_id)
            if not is_deleted:
                raise ResourceNotFoundError("Задача с таким ID не найдена в данном проекте")

            await self.uow.commit()
        
            await enqueue_task(
                self.arq_pool,
                "log_activity_task",
                user_id=current_user_id,
                project_id=project_id,
                action="task.deleted",
                resource_type="Task",
                resource_id=task_id,
                details=None
            )

            await clear_cache_key(self.redis, f"project:{project_id}:tasks_tree")
        