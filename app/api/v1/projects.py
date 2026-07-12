from fastapi import APIRouter, Depends, status

from app.api.dependencies.role import CheckProjectRole
from app.api.dependencies.uow import get_uow
from app.core.security import get_current_user
from app.models.project import Project
from app.models.project_member import Role
from app.models.user import User
from app.schemas.project import ProjectMemberAdd, ProjectCreate, ProjectResponse, ProjectUpdate
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
    
    return await project_service.create_new_project(project_data, current_user.id)

@router.post("/projects/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: int,
    member_data: ProjectMemberAdd,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER]))
):
    project_service = ProjectService(uow)
    await project_service.add_project_member(project_id, member_data)
    
    return {"detail": "Пользователь успешно добавлен в проект"}

@router.get("/projects", response_model=list[ProjectResponse])
async def get_my_projects(
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
) -> list[Project]:
    project_service = ProjectService(uow)
    
    return await project_service.get_my_projects(current_user.id)

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER]))
) -> Project:
    project_service = ProjectService(uow)
    
    return await project_service.update_project_details(project_id, project_data)
    
@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER]))
):
    project_service = ProjectService(uow)
    await project_service.delete_project(project_id)
