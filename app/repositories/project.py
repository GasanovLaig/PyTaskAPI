from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.project_member import ProjectMember, Role
from app.models.user import User
from app.repositories.base import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Project, session=session)

    async def create_project_with_user(self, project_data: dict, user: User) -> Project:
        new_project = Project(**project_data)
        new_project.memberships.append(ProjectMember(user_id=user.id, role=Role.OWNER))
        self.session.add(new_project)
        await self.session.commit()
        await self.session.refresh(new_project)
        
        return new_project
    
    async def get_user_role_in_project(self, project_id: int, user_id: int) -> Role:
        result = await self.session.scalars(
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        )
        member = result.first()
        
        return member.role if member else None

    async def get_user_projects(self, user: User) -> list[Project]:
        result = await self.session.scalars(
            select(Project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user.id)
        )
        
        return result.all()
