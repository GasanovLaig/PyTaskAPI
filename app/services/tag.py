from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.models.tag import Tag
from app.models.task import Task
from app.schemas.tag import TagCreate
from app.services.uow import UnitOfWork

class TagService:
    def __init__(self, uow: UnitOfWork, redis: Redis = None):
        self.uow = uow
        self.redis = redis
        
    async def create_new_tag(self, project_id: int, tag_data: TagCreate) -> Tag:
        async with self.uow:
            is_tag_exists = await self.uow.tags.is_tag_exists_by_name(
                project_id,
                tag_data.name
            )
            if is_tag_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Тег с таким именем уже существует"
                )
            
            tag_dict = tag_data.model_dump()
            tag_dict["project_id"] = project_id
            new_tag = await self.uow.tags.create(tag_dict)
            await self.uow.commit()
            
            return new_tag
    
    async def get_all_tags(self, project_id: int) -> list[Tag]:
        async with self.uow:
            return await self.uow.tags.get_all_tags_by_project(project_id)
    
    async def attach_tag_to_task(self, project_id: int, task_id: int, tag_id: int) -> Task:
        async with self.uow:
            task = await self.uow.tasks.get_with_tags(task_id)
            if task is None or task.project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Задача с таким ID не найдена в данном проекте"
                )
            
            tag = await self.uow.tags.get_by_id_secure(tag_id, project_id)
            if not tag:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Тег с таким ID не найден в данном проекте"
                )
            
            if tag_id in {tag.id for tag in task.tags}:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Тег с таким названием уже прикреплен к этой задаче"
                )
            
            task.tags.append(tag)
            await self.uow.commit()
            await self.redis.delete(f"project:{project_id}:tasks_tree")
            
            return task
    
    async def delete_tag_by_id(self, project_id: int, tag_id: int):
        async with self.uow:
            deleted = await self.uow.tags.delete_by_id_secure(tag_id, project_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Тег с таким ID не найден в данном проекте"
                )
            
            await self.uow.commit()
            await self.redis.delete(f"project:{project_id}:tasks_tree")
        