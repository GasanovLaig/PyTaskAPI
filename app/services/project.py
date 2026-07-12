from fastapi import HTTPException, status

from app.models.project import Project
from app.schemas.project import ProjectMemberAdd, ProjectCreate, ProjectUpdate
from app.services.uow import UnitOfWork

class ProjectService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_project(self, project_data: ProjectCreate, current_user_id: id) -> Project:
        async with self.uow:
            project_dict = project_data.model_dump()
            new_project = await self.uow.projects.create_project_with_user(project_dict, current_user_id)
            await self.uow.commit()

            return new_project
                  
    async def add_project_member(self, project_id: int, member_data: ProjectMemberAdd):
        async with self.uow:
            is_user_exists = await self.uow.users.is_exists(member_data.user_id)
            if not is_user_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь с таким ID не найден"
                )
                
            is_already_member = await self.uow.projects.is_member(project_id, member_data.user_id)
            if is_already_member:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким ID уже состоит в проекте"
                )
                
            db_data = member_data.model_dump()
            db_data["project_id"] = project_id
            await self.uow.projects.add_project_member(db_data)
            await self.uow.commit()

    async def get_my_projects(self, current_user_id: int) -> list[Project]:
        async with self.uow:
            return await self.uow.projects.get_my_projects(current_user_id)
    
    async def update_project_details(self, project_id: int, project_data: ProjectUpdate) -> Project:
        async with self.uow:
            update_dict = project_data.model_dump(exclude_unset=True)
            updated_project = await self.uow.projects.update_by_id(project_id, update_dict)
            await self.uow.commit()
            
            return updated_project
    
    async def delete_project(self, project_id: int):
        async with self.uow:
            deleted = await self.uow.projects.delete_by_id(project_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Проект с таким ID не найден"
                )
            
            await self.uow.commit()
    