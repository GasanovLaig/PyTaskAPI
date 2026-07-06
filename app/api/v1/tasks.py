from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.api.dependencies.role import CheckProjectRole
from app.api.dependencies.uow import get_uow
from app.core.redis_client import get_redis
from app.services.uow import UnitOfWork
from app.models.project_member import Role
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskTreeResponse, TaskUpdate
from app.services.task import TaskService

router = APIRouter(tags=["Задачи"])

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: int,
    task_data: TaskCreate,
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> Task:
    task_service = TaskService(uow, redis)
    
    return await task_service.create_task(project_id, task_data)

@router.get("/projects/{project_id}/tasks/tree", response_model=list[TaskTreeResponse])
async def get_project_tasks_tree(
    project_id: int,
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
) -> list[Task]:
    task_service = TaskService(uow, redis)
    
    return await task_service.get_project_tasks_tree(project_id)

@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    project_id: int,
    task_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
) -> Task:
    task_service = TaskService(uow)
    
    return await task_service.get_task_by_id(project_id, task_id)

@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def get_project_tasks(
    project_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
) -> list[Task]:
    task_service = TaskService(uow)
    
    return await task_service.get_project_tasks(project_id)

@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> Task:
    task_service = TaskService(uow, redis)
    
    return await task_service.update_task_details(
        project_id,
        task_id,
        task_data
    )

@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    project_id: int,
    task_id: int,
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> None:
    task_service = TaskService(uow, redis)
    await task_service.delete_task(project_id, task_id)
    
    return None
