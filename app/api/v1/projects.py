from arq import ArqRedis
from arq.jobs import Job
from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.models.project import Project
from app.services.uow import UnitOfWork
from app.models.project_member import Role
from app.api.dependencies.uow import get_uow
from app.core.security import get_current_user
from app.services.project import ProjectService
from app.api.dependencies.arq import get_arq_pool
from app.api.dependencies.role import CheckProjectRole
from app.schemas.project import (
    ProjectMemberAdd,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ReportStatusResponse,
    ReportTaskResponse
)
from app.utils.enqueue_task import enqueue_task

router = APIRouter(tags=["Проекты"])

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user),
    arq_pool: ArqRedis = Depends(get_arq_pool)
) -> Project:
    project_service = ProjectService(uow, arq_pool)
    
    return await project_service.create_new_project(project_data, current_user.id)

@router.post("/projects/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: int,
    member_data: ProjectMemberAdd,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(CheckProjectRole([Role.OWNER])),
    arq_pool: ArqRedis = Depends(get_arq_pool)
):
    project_service = ProjectService(uow, arq_pool)
    await project_service.add_project_member(project_id, member_data, current_user.id)
    
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
    current_user: User = Depends(CheckProjectRole([Role.OWNER])),
    arq_pool: ArqRedis = Depends(get_arq_pool)
) -> Project:
    project_service = ProjectService(uow, arq_pool)
    
    return await project_service.update_project_details(project_id, project_data, current_user.id)
    
@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(CheckProjectRole([Role.OWNER])),
    arq_pool: ArqRedis = Depends(get_arq_pool)
):
    project_service = ProjectService(uow, arq_pool)
    await project_service.delete_project(project_id, current_user.id)
    
@router.post(
    "/projects/{project_id}/reports",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ReportTaskResponse,
    tags=["Отчеты"]
)
async def request_project_report(
    project_id: int,
    arq_pool: ArqRedis = Depends(get_arq_pool),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
):
    job = await enqueue_task(
        arq_pool,
        "generate_project_report_task",
        suppress_errors=False,
        project_id=project_id
    )
    job_status = await job.status()
    
    return ReportTaskResponse(
        task_id=job.job_id,
        status=job_status
    )
    
@router.get(
    "/projects/{project_id}/reports/status/{task_id}",
    response_model=ReportStatusResponse,
    tags=["Отчеты"]
)
async def get_report_status(
    project_id: int,
    task_id: str,
    arq_pool: ArqRedis = Depends(get_arq_pool),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
):
    job = Job(task_id, arq_pool)
    job_status = await job.status()
    
    result_data = None
    if job_status == "complete":
        result_data = await job.result()
        
    return ReportStatusResponse(
        task_id=task_id,
        status=job_status,
        result=result_data
    )
    