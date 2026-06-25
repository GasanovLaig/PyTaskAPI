from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.models.task import Task
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Task, session=session)
        
    async def create_task(self, task_data: dict) -> Task:
        new_task = Task(**task_data)
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task, attribute_names=["tags"])
        
        return new_task
    
    async def attach_tag(self, task: Task, tag: Tag) -> Task:
        await self.session.refresh(task, attribute_names=["tags"])
        if tag in task.tags:
            raise HTTPException(status_code=409, detail="Тег с таким названием уже прикреплен к задаче")
            
        task.tags.append(tag)
        await self.session.commit()
        await self.session.refresh(task, attribute_names=["tags"])
        
        return task
        