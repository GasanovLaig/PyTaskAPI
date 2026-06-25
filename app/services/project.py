from fastapi import HTTPException

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.project import ProjectCreate

class ProjectService:
    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository):
        self.project_repo = project_repo
        self.user_repo = user_repo
        
    async def create_new_project(self, user_id: int, project_data: ProjectCreate) -> Project:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь с таким ID не найден")
        
        project_dict = project_data.model_dump()
        
        return await self.project_repo.create_project_with_user(project_data=project_dict, user=user)

    async def get_projects_by_user(self, user_id: int) -> list[Project]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь с таким ID не найден")
        
        return await self.project_repo.get_user_projects(user_id=user_id)
    