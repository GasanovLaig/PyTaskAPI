from fastapi import APIRouter, Depends

from app.api.dependencies.uow import get_uow
from app.models.tag import Tag
from app.models.task import Task
from app.schemas.task import TaskResponse
from app.services.tag import TagService
from app.schemas.tag import TagCreate, TagResponse
from app.services.uow import UnitOfWork

router = APIRouter(tags=["Теги"])

@router.post("/tags", response_model=TagResponse)
async def create_tag(
    data: TagCreate,
    uow: UnitOfWork = Depends(get_uow)
) -> Tag:
    tag_service = TagService(uow)
    
    return await tag_service.create_new_tag(data)

@router.get("/tags", response_model=list[TagResponse])
async def get_all_tags(
    uow: UnitOfWork = Depends(get_uow)
) -> list[Tag]:
    tag_service = TagService(uow)
    
    return await tag_service.get_all_tags()

@router.put("/tasks/{task_id}/tags/{tag_id}", response_model=TaskResponse)
async def attach_tag_to_task(
    task_id: int,
    tag_id: int,
    uow: UnitOfWork = Depends(get_uow)
) -> Task:
    tag_service = TagService(uow)
    
    return await tag_service.attach_tag_to_task(task_id, tag_id)

@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    uow: UnitOfWork = Depends(get_uow)
) -> None:
    tag_service = TagService(uow)
    await tag_service.delete_tag_by_id(tag_id)
    
    return None
