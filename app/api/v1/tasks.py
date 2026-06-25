from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.task import Task
from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.tag import TagRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.services.comment import CommentService
from app.services.tag import TagService
from app.services.task import TaskService

router = APIRouter(tags=["Задачи и Обсуждения"])

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db)
) -> Task:
    task_repository = TaskRepository(session=db)
    project_repository = ProjectRepository(session=db)
    user_repository = UserRepository(session=db)
    
    task_service = TaskService(
        task_repo=task_repository,
        project_repo=project_repository,
        user_repo=user_repository
    )
    
    return await task_service.create_task(project_id=project_id, task_data=data)

@router.post("/tags", response_model=TagResponse)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)) -> Tag:
    tag_repository = TagRepository(session=db)
    task_repository = TaskRepository(session=db)
    
    tag_service = TagService(
        tag_repo=tag_repository,
        task_repo=task_repository
    )
    
    return await tag_service.create_new_tag(tag_data=data)

@router.put("/tasks/{task_id}/tags/{tag_id}", response_model=TaskResponse)
async def attach_tag_to_task(task_id: int, tag_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    tag_repository = TagRepository(session=db)
    task_repository = TaskRepository(session=db)
    
    tag_service = TagService(
        tag_repo=tag_repository,
        task_repo=task_repository
    )
    
    return await tag_service.attach_tag_to_task(task_id=task_id, tag_id=tag_id)

@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
async def create_comment(task_id: int, data: CommentCreate, db: AsyncSession = Depends(get_db)) -> Comment:
    comment_repository = CommentRepository(session=db)
    task_repository = TaskRepository(session=db)
    author_repository = UserRepository(session=db)
    
    comment_service = CommentService(
        comment_repo=comment_repository,
        task_repo=task_repository,
        author_repo=author_repository
    )
    
    return await comment_service.create_new_comment(task_id=task_id, comment_data=data)
