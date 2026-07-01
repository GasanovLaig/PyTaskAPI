from fastapi import APIRouter, Depends

from app.api.dependencies.uow import get_uow
from app.core.security import get_current_user
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService
from app.services.uow import UnitOfWork

router = APIRouter(tags=["Проекты"])

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
) -> Project:
    project_service = ProjectService(uow)
    
    return await project_service.create_new_project(current_user.id, project_data)

@router.get("/users/{user_id}/projects", response_model=list[ProjectResponse])
async def get_projects_by_user(
    user_id: int,
    uow: UnitOfWork = Depends(get_uow)
) -> list[Project]:
    project_service = ProjectService(uow)
    
    return await project_service.get_projects_by_user(user_id)

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
) -> Project:
    project_service = ProjectService(uow)
    
    return await project_service.update_project_details(
        project_id,
        current_user.id,
        project_data
    )
    
@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
) -> None:
    project_service = ProjectService(uow)
    await project_service.delete_project(
        project_id,
        current_user.id
    )
    
    return None
