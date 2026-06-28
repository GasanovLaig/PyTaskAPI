from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    
    async def get_with_tags(self, task_id: int) -> Task | None:
        return await self.get_by_id(
            obj_id=task_id,
            options=[selectinload(Task.tags)]
        )
    
    async def attach_tag(self, task: Task, tag: Tag) -> Task:
        await self.session.refresh(task, attribute_names=["tags"])
        if tag in task.tags:
            raise HTTPException(status_code=409, detail="Тег с таким названием уже прикреплен к задаче")
            
        task.tags.append(tag)
        await self.session.commit()
        await self.session.refresh(task, attribute_names=["tags"])
        
        return task
    
    async def get_tasks_by_project(self, project_id: int) -> list[Task]:
        result = await self.session.scalars(
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.tags))
        )
        
        return result.all()
        