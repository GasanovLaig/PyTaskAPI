from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError

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
            db_data = tag_data.model_dump()
            db_data["project_id"] = project_id
            try:
                new_tag = await self.uow.tags.create(db_data)
                await self.uow.commit()
                
                return new_tag
            
            except IntegrityError:
                await self.uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Тег с таким названием уже существует в данном проекте"
                )
    
    async def get_all_tags(self, project_id: int) -> list[Tag]:
        async with self.uow:
            return await self.uow.tags.get_all_tags_by_project(project_id)
    
    async def attach_tag_to_task(self, project_id: int, task_id: int, tag_id: int) -> None:
        async with self.uow:
            try:
                is_attached = await self.uow.tags.attach_tag_secure(
                    project_id,
                    task_id,
                    tag_id
                )
                
                if not is_attached:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Задача или тег с таким ID не найдены в данном проекте"
                    )
                
                await self.uow.commit()
                
            except IntegrityError:
                await self.uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Этот тег уже прикреплен к данной задаче"
                )
                
            await self.redis.delete(f"project:{project_id}:tasks_tree")
    
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
        