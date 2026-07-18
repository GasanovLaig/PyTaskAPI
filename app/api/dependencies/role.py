from fastapi import Depends

from app.api.dependencies.uow import get_uow
from app.core.exceptions import ResourceNotFoundError
from app.core.security import get_current_user
from app.models.project_member import Role
from app.models.user import User
from app.services.uow import UnitOfWork

class CheckProjectRole:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles
        
    async def __call__(
        self,
        project_id: int,
        current_user: User = Depends(get_current_user),
        uow: UnitOfWork = Depends(get_uow),
    ) -> User:
        async with uow:
            user_role = await uow.projects.get_user_role_in_project(
                project_id,
                current_user.id
            )
            
            if user_role == Role.OWNER or (user_role is not None and user_role in self.allowed_roles):
                return current_user

            raise ResourceNotFoundError("Проект не найден или у вас нет к нему доступа")
    