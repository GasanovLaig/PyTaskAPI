from app.core.events import event_bus
from app.models.project import Project
from app.services.uow import UnitOfWork
from app.core.exceptions import ResourceNotFoundError
from app.schemas.project import ProjectMemberAdd, ProjectCreate, ProjectUpdate
from app.events.events import (
    ProjectCreatedEvent, ProjectDeletedEvent,
    ProjectMemberAddedEvent, ProjectUpdatedEvent
)

class ProjectService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def create_new_project(self, project_data: ProjectCreate, current_user_id: int) -> Project:
        async with self.uow:
            project_dict = project_data.model_dump()
            new_project = await self.uow.projects.create_project_with_user(project_dict, current_user_id)
            await self.uow.commit()
            
        await event_bus.publish(
            ProjectCreatedEvent(
                project_id=new_project.id,
                project_title=new_project.title,
                current_user_id=current_user_id
            ))

        return new_project
                  
    async def add_project_member(self, project_id: int, member_data: ProjectMemberAdd, current_user_id: int):
        async with self.uow:
            db_data = member_data.model_dump()
            db_data["project_id"] = project_id
            await self.uow.projects.add_project_member(db_data)
            await self.uow.commit()
            
        await event_bus.publish(
            ProjectMemberAddedEvent(
                project_id=project_id,
                user_id=member_data.user_id,
                role=member_data.role.value,
                current_user_id=current_user_id
            ))
            
    async def get_my_projects(self, current_user_id: int) -> list[Project]:
        async with self.uow:
            return await self.uow.projects.get_my_projects(current_user_id)
    
    async def update_project_details(self, project_id: int, project_data: ProjectUpdate, current_user_id: int) -> Project:
        async with self.uow:
            db_data = project_data.model_dump(exclude_unset=True)
            updated_project = await self.uow.projects.update_by_id(project_id, db_data)
            if not updated_project:
                raise ResourceNotFoundError("Проект с таким ID не найден")
            
            await self.uow.commit()
            
        await event_bus.publish(
            ProjectUpdatedEvent(
                project_id=project_id,
                current_user_id=current_user_id,
                updated_fields=list(db_data.keys())
            ))
        
        return updated_project
    
    async def delete_project(self, project_id: int, current_user_id: int):
        async with self.uow:
            is_deleted = await self.uow.projects.delete_by_id(project_id)
            if not is_deleted:
                raise ResourceNotFoundError("Проект с таким ID не найден")
            
            await self.uow.commit()
            
        await event_bus.publish(ProjectDeletedEvent(project_id, current_user_id))
        