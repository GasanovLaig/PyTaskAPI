from typing import Any

from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_member import ProjectMember, Role
from app.repositories.base import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Project, session=session)

    async def create_project_with_user(self, project_data: dict, current_user_id: int) -> Project:
        new_project = Project(**project_data)
        new_project.memberships.append(ProjectMember(user_id=current_user_id, role=Role.OWNER))
        self.session.add(new_project)
        
        return new_project
    
    async def add_project_member(self, member_data: dict[str, Any]):
        await self.session.execute(
            insert(ProjectMember)
            .values(**member_data)
        )
    
    async def get_user_role_in_project(self, project_id: int, user_id: int) -> Role:
        role = await self.session.scalar(
            select(ProjectMember.role)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        )
        
        return role

    async def get_my_projects(self, current_user_id: int) -> list[Project]:
        result = await self.session.scalars(
            select(Project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == current_user_id)
        )
        
        return result.all()
    
    async def is_member(self, project_id: int, user_id: int) -> bool:
        result = await self.session.scalar(
            select(exists().where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )))
        
        return bool(result)
