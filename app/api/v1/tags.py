from fastapi import APIRouter, Depends, status

from app.api.dependencies.role import CheckProjectRole
from app.api.dependencies.uow import get_uow
from app.models.project_member import Role
from app.models.tag import Tag
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskResponse
from app.services.tag import TagService
from app.schemas.tag import TagCreate, TagResponse
from app.services.uow import UnitOfWork

router = APIRouter(tags=["Теги"])

@router.post("/projects/{project_id}/tags", response_model=TagResponse)
async def create_tag(
    project_id: int,
    tag_data: TagCreate,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> Tag:
    tag_service = TagService(uow)
    
    return await tag_service.create_new_tag(project_id, tag_data)

@router.get("/projects/{project_id}/tags", response_model=list[TagResponse])
async def get_all_tags(
    project_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
) -> list[Tag]:
    tag_service = TagService(uow)
    
    return await tag_service.get_all_tags(project_id)

@router.put("/project/{project_id}/tasks/{task_id}/tags/{tag_id}", response_model=TaskResponse)
async def attach_tag_to_task(
    project_id: int,
    task_id: int,
    tag_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> Task:
    tag_service = TagService(uow)
    
    return await tag_service.attach_tag_to_task(project_id, task_id, tag_id)

@router.delete("/projects/{project_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    project_id: int,
    tag_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
):
    tag_service = TagService(uow)
    await tag_service.delete_tag_by_id(project_id, tag_id)
