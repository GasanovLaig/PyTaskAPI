from redis.asyncio import Redis

from app.models.tag import Tag
from app.schemas.tag import TagCreate
from app.services.uow import UnitOfWork
from app.core.exceptions import ResourceNotFoundError
from app.utils.clear_cache_key import clear_cache_key

class TagService:
    def __init__(self, uow: UnitOfWork, redis: Redis = None):
        self.uow = uow
        self.redis = redis
        
    async def create_new_tag(self, project_id: int, tag_data: TagCreate) -> Tag:
        async with self.uow:
            db_data = tag_data.model_dump()
            db_data["project_id"] = project_id
            new_tag = await self.uow.tags.create(db_data)
            await self.uow.commit()
            
        return new_tag
    
    async def get_all_tags(self, project_id: int) -> list[Tag]:
        async with self.uow:
            return await self.uow.tags.get_all_tags_by_project(project_id)
    
    async def attach_tag_to_task(self, project_id: int, task_id: int, tag_id: int) -> None:
        async with self.uow:
            is_attached = await self.uow.tags.attach_tag_to_task_secure(
                project_id,
                task_id,
                tag_id
            )
            if not is_attached:
                raise ResourceNotFoundError("Задача или тег с таким ID не найдены в данном проекте")
            
            await self.uow.commit()
                
        await clear_cache_key(self.redis, f"project:{project_id}:tasks_tree")
            
    async def detach_tag_from_task(self, project_id: int, task_id: int, tag_id: int) -> None:
        async with self.uow:
            is_deleted = await self.uow.tags.delete_tag_from_task(project_id, task_id, tag_id)
            if not is_deleted:
                raise ResourceNotFoundError("Задача или тег с таким ID не найдены в данном проекте")
                
            await self.uow.commit()
            
        await clear_cache_key(self.redis, f"project:{project_id}:tasks_tree")
    
    async def delete_tag_by_id(self, project_id: int, tag_id: int) -> None:
        async with self.uow:
            is_deleted = await self.uow.tags.delete_by_id_secure(tag_id, project_id)
            if not is_deleted:
                raise ResourceNotFoundError("Тег с таким ID не найден в данном проекте")

            await self.uow.commit()
            
        await clear_cache_key(self.redis, f"project:{project_id}:tasks_tree")
        