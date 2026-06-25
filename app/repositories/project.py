from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Project, session=session)
        
    async def get_user_projects(self, user_id: int) -> list[Project]:
        result = await self.session.execute(
            select(User).filter(User.id == user_id)
        )
        
        user = result.scalar_one_or_none()
        if user:
            await self.session.refresh(user, ["projects"])
            return list(user.projects)
        
        return []
    