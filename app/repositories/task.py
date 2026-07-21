from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Task, session=session)
        
    async def get_task_with_tags_secure(self, project_id: int, task_id: int) -> Task | None:
        return await self.session.scalar(
            select(Task)
            .where(
                Task.id == task_id,
                Task.project_id == project_id
            )
            .options(selectinload(Task.tags))
        )
    
    async def get_tasks_by_project(self, project_id: int) -> list[Task]:
        result = await self.session.scalars(
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.tags))
        )
        
        return result.all()
    
    async def get_project_tasks_tree(self, project_id: int) -> list[Task]:
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
    
    async def get_metadata_for_celery(self, project_id: int, performer_id: int) -> tuple[str, str]:
        result = await self.session.execute(
            select(User.email, Project.title)
            .where(
                User.id == performer_id,
                Project.id == project_id
            )
        )
        
        return result.fetchone()
    
    async def get_task_log_metadata_secure(self, project_id: int, task_id: int) -> tuple[str, str, int | None] | None:
        """
        Вытаскивает из базы строго три поля для сверки истории аудита и защиты от IDOR.
        Возвращает кортеж (title, status, performer_id) или None, если задача не найдена.
        """
        result = await self.session.execute(
            select(Task.title, Task.status, Task.performer_id)
            .where(
                Task.id == task_id,
                Task.project_id == project_id
            )
        )
        
        return result.fetchone()
    