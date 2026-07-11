from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
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
            await self.uow.projects.delete_by_id(project_id)
            await self.uow.commit()
    