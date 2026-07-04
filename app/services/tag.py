from fastapi import HTTPException

from app.models.tag import Tag
from app.models.task import Task
from app.schemas.tag import TagCreate
from app.services.uow import UnitOfWork

class TagService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_tag(self, tag_data: TagCreate) -> Tag:
        async with self.uow:
            exisiting_tag = await self.uow.tags.get_by_name(tag_data.name)
            if exisiting_tag:
                raise HTTPException(status_code=409, detail="Тег с таким именем уже существует")
            
            new_tag = await self.uow.tags.create(tag_data.model_dump())
            await self.uow.commit()
            await self.uow.refresh(new_tag)
            
            return new_tag
    
    async def get_all_tags(self) -> list[Tag]:
        async with self.uow:
            return await self.uow.tags.get_all()
    
    async def attach_tag_to_task(self, project_id: int, task_id: int, tag_id: int) -> Task:
        async with self.uow:
            task = await self.uow.tasks.get_by_id(task_id)
            if task is None or task.project_id != project_id:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена в данном проекте")
            
            tag = await self.uow.tags.get_by_id(tag_id)
            if tag is None:
                raise HTTPException(status_code=404, detail="Тег с таким ID не найден")
            
            task_with_tag = await self.uow.tasks.attach_tag(task, tag)
            await self.uow.commit()
            
            return task_with_tag
    
    async def delete_tag_by_id(self, tag_id: int) -> None:
        async with self.uow:
            tag = await self.uow.tags.get_by_id(tag_id)
            if not tag:
                raise HTTPException(status_code=404, detail="Тег с таким ID не найден")
            
            await self.uow.tags.delete(tag)
            await self.uow.commit()
            
            return None
        