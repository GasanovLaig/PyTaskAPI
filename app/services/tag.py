from fastapi import HTTPException

from app.models.tag import Tag
from app.models.task import Task
from app.repositories.tag import TagRepository
from app.repositories.task import TaskRepository
from app.schemas.tag import TagCreate

class TagService:
    def __init__(self, tag_repo: TagRepository, task_repo: TaskRepository):
        self.tag_repo = tag_repo
        self.task_repo = task_repo
        
    async def create_new_tag(self, tag_data: TagCreate) -> Tag:
        exisiting_tag = await self.tag_repo.get_by_name(tag_data.name)
        if exisiting_tag:
            raise HTTPException(status_code=409, detail="Тег с таким именем уже существует")
        
        return await self.tag_repo.create(tag_data.model_dump())
    
    async def attach_tag_to_task(self, task_id: int, tag_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
        
        tag = await self.tag_repo.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(status_code=404, detail="Тег с таким ID не найден")
        
        return await self.task_repo.attach_tag(task, tag)
    