from fastapi import HTTPException

from app.models.tag import Tag
from app.models.task import Task
from app.schemas.tag import TagCreate
from app.services.uow import UnitOfWork

class TagService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_tag(self, project_id: int, tag_data: TagCreate) -> Tag:
        async with self.uow:
            is_tag_exists = await self.uow.tags.get_by_name(project_id, tag_data.name)
            if is_tag_exists:
                raise HTTPException(status_code=409, detail="Тег с таким именем уже существует")
            
            tag_dict = tag_data.model_dump()
            tag_dict["project_id"] = project_id
            # TODO: оптимизировать refresh, flush, returning
            new_tag = await self.uow.tags.create(tag_dict)
            await self.uow.commit()
            await self.uow.refresh(new_tag)
            
            return new_tag
    
    async def get_all_tags(self, project_id: int) -> list[Tag]:
        async with self.uow:
            return await self.uow.tags.get_all_tags_by_project(project_id)
    
    async def attach_tag_to_task(self, project_id: int, task_id: int, tag_id: int) -> Task:
        async with self.uow:
            task = await self.uow.tasks.get_by_id(task_id)
            if task is None or task.project_id != project_id:
                raise HTTPException(status_code=404, detail="Задача с таким ID не найдена в данном проекте")
            
            tag = await self.uow.tags.get_by_id(tag_id)
            if tag is None or tag.project_id != project_id:
                raise HTTPException(status_code=404, detail="Тег с таким ID не найден в данном проекте")
            
            task_with_tag = await self.uow.tasks.attach_tag(task, tag)
            await self.uow.commit()
            
            return task_with_tag
    
    async def delete_tag_by_id(self, project_id: int, tag_id: int) -> None:
        async with self.uow:
            tag = await self.uow.tags.get_by_id(tag_id)
            if not tag or tag.project_id != project_id:
                raise HTTPException(status_code=404, detail="Тег с таким ID не найден в данном проекте")
            
            await self.uow.tags.delete(tag)
            await self.uow.commit()
            
            return None
        