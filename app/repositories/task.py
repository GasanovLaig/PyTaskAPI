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
        await self.session.flush()
        
        return await self.get_with_tags(new_task.id)
    
    async def get_with_tags(self, task_id: int) -> Task | None:
        return await self.get_by_id(
            obj_id=task_id,
            options=[selectinload(Task.tags)],
            populate_existing=True
        )
    
    async def attach_tag(self, task: Task, tag: Tag) -> Task:
        task_with_tags = await self.get_with_tags(task.id)
        if task_with_tags is not None:
            raise HTTPException(status_code=404, detail="Задача с таким ID не найдена")
        
        if tag in task_with_tags.tags:
            raise HTTPException(status_code=409, detail="Тег с таким названием уже прикреплен к задаче")
        
        task_with_tags.tags.append(tag)
        
        return task_with_tags
    
    async def get_tasks_by_project(self, project_id: int) -> list[Task]:
        result = await self.session.scalars(
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.tags))
        )
        
        return result.all()
    
    async def get_project_task_tree(self, project_id: int) -> list[Task]:
        start_cte = select(Task.id).where(
            Task.project_id == project_id,
            Task.parent_task_id == None
        ).cte(name="task_tree", recursive=True)
        
        recursive_cte = start_cte.union_all(
            select(Task.id).where(Task.parent_task_id == start_cte.c.id)
        )
        
        result = await self.session.scalars(
            select(Task)
            .where(Task.id.in_(select(recursive_cte.c.id)))
            .options(
                selectinload(Task.tags),
                selectinload(Task.subtasks)
            )
        )
        
        all_tasks = result.all()
        
        return [task for task in all_tasks if task.parent_task_id is None]
