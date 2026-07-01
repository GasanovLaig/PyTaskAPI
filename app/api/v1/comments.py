from fastapi import APIRouter, Depends

from app.api.dependencies.uow import get_uow
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment import CommentService
from app.services.uow import UnitOfWork

router = APIRouter(tags=["Комментарии"])

@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
async def create_comment(
    task_id: int,
    data: CommentCreate,
    uow: UnitOfWork = Depends(get_uow)
) -> Comment:
    comment_service = CommentService(uow)
    
    return await comment_service.create_new_comment(task_id, data)

@router.get("/projects/{project_id}/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    project_id: int,
    task_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
) -> list[Comment]:
    comment_service = CommentService(uow)
    
    return await comment_service.get_task_comments(
        project_id=project_id,
        task_id=task_id,
        user_id=current_user.id
    )
    
@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
) -> None:
    comment_service = CommentService(uow)
    await comment_service.delete_comment_by_id(comment_id, current_user.id)
    
    return None
