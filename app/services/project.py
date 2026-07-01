from fastapi import HTTPException

from app.models.project import Project
from app.models.project_member import Role
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.uow import UnitOfWork

class ProjectService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_project(self, user_id: int, project_data: ProjectCreate) -> Project:
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь с таким ID не найден")
            
            project_dict = project_data.model_dump()
            new_project = await self.uow.projects.create_project_with_user(project_data=project_dict, user=user)
            await self.uow.commit()
            await self.uow.refresh(new_project)
            
            return new_project

    async def get_projects_by_user(self, user_id: int) -> list[Project]:
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь с таким ID не найден")
            
            return await self.uow.projects.get_user_projects(user)
    
    async def update_project_details(self, project_id: int, user_id: int, project_data: ProjectUpdate) -> Project:
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Проекта с таким ID не найден")
            
            user_role = await self.uow.projects.get_user_role_in_project(project_id, user_id)
            if user_role != Role.OWNER:
                raise HTTPException(status_code=403, detail="Только владелец может редактировать проект")
            
            update_dict = project_data.model_dump(exclude_unset=True)
            
            updated_project = await self.uow.projects.update(project, update_dict)
            await self.uow.commit()
            
            return updated_project
    
    async def delete_project(self, project_id: int, user_id: int) -> None:
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Проект с таким ID не найден")
            
            user_role = await self.uow.projects.get_user_role_in_project(project_id, user_id)
            if not user_role:
                raise HTTPException(status_code=403, detail="Только владелец может редактировать проект")
            
            await self.uow.projects.delete(project)
            await self.uow.commit()
            
            return None
    