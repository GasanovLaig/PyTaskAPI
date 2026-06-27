from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.project_member import Role
from app.models.user import User
from app.repositories.project import ProjectRepository

class CheckProjectRole:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles
        
    async def __call__(
        self,
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        project_repo = ProjectRepository(session=db)
        
        user_role = await project_repo.get_user_role_in_project(
            project_id,
            current_user.id
        )

        if user_role is None or user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этого действия в проекте"
            )
            
        return current_user
    