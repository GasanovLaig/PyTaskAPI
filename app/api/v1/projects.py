from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.project import Project
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter(tags=["Проекты"])

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Project:
    user_repository = UserRepository(session=db)
    project_repository = ProjectRepository(session=db)
    project_service = ProjectService(project_repo=project_repository, user_repo=user_repository)
    
    return await project_service.create_new_project(user_id=current_user.id, project_data=project_data)

@router.get("/users/{user_id}/projects", response_model=list[ProjectResponse])
async def get_projects_by_user(user_id: int, db: AsyncSession = Depends(get_db)) -> list[Project]:
    user_repository = UserRepository(session=db)
    project_repository = ProjectRepository(session=db)
    project_service = ProjectService(user_repo=user_repository, project_repo=project_repository)
    
    return await project_service.get_projects_by_user(user_id=user_id)

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project_repository = ProjectRepository(session=db)
    user_repository = UserRepository(session=db)
    project_service = ProjectService(project_repo=project_repository, user_repo=user_repository)
    
    return await project_service.update_project_details(
        project_id=project_id,
        user_id=current_user.id,
        project_data=data
    )
