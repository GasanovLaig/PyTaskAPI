from sqlalchemy.orm import selectinload
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Task, session=session)
        
    async def create_and_get_notify_metadata(self, db_data: dict) -> tuple[Task, dict]:
        """Создает задачу и ОДНИМ запросом возвращает её вместе с данными для уведомлений."""
        new_task = await self.session.scalar(
            insert(Task)
            .values(**db_data)
            .returning(Task)
        )
        
        notify_metadata = {"performer_email": None, "project_title": None}
        
        result = await self.session.execute(
            select(User.email, Project.title)
            .select_from(Task)
            .join(Project, Project.id == Task.project_id)
            .outerjoin(User, User.id == Task.performer_id)
            .where(Task.id == new_task.id)
        )
        row = result.fetchone()
        if row:
            performer_email, project_title = row
            notify_metadata["performer_email"] = performer_email
            notify_metadata["project_title"] = project_title
            
        return new_task, notify_metadata
        
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
    
    async def get_task_log_metadata_secure(self, project_id: int, task_id: int) -> tuple[str, str, int | None] | None:
        result = await self.session.execute(
            select(Task.title, Task.status, Task.performer_id)
            .where(
                Task.id == task_id,
                Task.project_id == project_id
            )
        )
        
        return result.fetchone()
    
    async def search_tasks_in_project(self, project_id: int, search_query: str) -> list[Task] | None:
        """Быстрый лингвистический поиск по задачам проекта с использованием готового TSVECTOR."""
        
        result = await self.session.scalars(
            select(Task)
            .where(
                Task.project_id == project_id,
                Task.search_vector.match(search_query, postgresql_regconfig="russian")
            )
            .options(selectinload(Task.tags))
        )
        
        return result.all()
    
    async def update_and_get_all_metadata(self, task_id: int, project_id: int, db_data: dict) -> tuple[Task, dict, dict]:
        """Обновляет задачу и ОДНИМ запросом возвращает её состояние вместе со связанными данными."""
        query = (
            select(Task.title, Task.status, Task.performer_id, User.email, Project.title)
            .join(Project, Project.id == Task.project_id)
            .outerjoin(User, User.id == Task.performer_id)
            .where(
                Task.id == task_id,
                Task.project_id == project_id
            )
            .with_for_update(of=[Task, Project])
        )
        
        result = await self.session.execute(query)
        row = result.fetchone()
        if not row:
            return None, None, None
        
        old_title, old_status, old_performer_id, performer_email, project_title = row
        old_metadata = {
            "title": old_title,
            "status": old_status,
            "performer_id": old_performer_id
        }
        
        updated_task = await self.session.scalar(
            update(Task)
            .where(
                Task.project_id == project_id,
                Task.id == task_id
            )
            .values(**db_data)
            .returning(Task)
        )
        
        notify_metadata = {
            "performer_email": performer_email,
            "project_title": project_title
        }
        
        return updated_task, old_metadata, notify_metadata
        