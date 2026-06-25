from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.repositories.base import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Project, session=session)

    async def create_project_with_user(self, project_data: dict, user: User) -> Project:
        new_project = Project(**project_data)
        new_project.users.append(user)
        self.session.add(new_project)
        await self.session.commit()
        await self.session.refresh(new_project)
        
        return new_project

    async def get_user_projects(self, user_id: int) -> list[Project]:
        result = await self.session.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            await self.session.refresh(user, ["projects"])
            return list(user.projects)
        
        return []
