from fastapi import APIRouter, Depends

from app.api.dependencies.role import CheckProjectRole
from app.api.dependencies.uow import get_uow
from app.models.comment import Comment
from app.models.project_member import Role
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment import CommentService
from app.services.uow import UnitOfWork

router = APIRouter(tags=["Комментарии"])

@router.post("/projects/{project_id}/tasks/{task_id}/comments", response_model=CommentResponse)
async def create_comment(
    project_id: int,
    task_id: int,
    comment_data: CommentCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
) -> Comment:
    comment_service = CommentService(uow)
    
    return await comment_service.create_new_comment(
        project_id,
        task_id,
        current_user.id,
        comment_data
    )

@router.get("/projects/{project_id}/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    project_id: int,
    task_id: int,
    uow: UnitOfWork = Depends(get_uow),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> list[Comment]:
    comment_service = CommentService(uow)
    
    return await comment_service.get_task_comments(project_id, task_id)
    
@router.delete("/projects/{project_id}/tasks/{task_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    project_id: int,
    comment_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER, Role.DEVELOPER]))
) -> None:
    comment_service = CommentService(uow)
    await comment_service.delete_comment_by_id(project_id, comment_id, current_user.id)
    
    return None
