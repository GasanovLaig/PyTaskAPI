from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.role import CheckProjectRole
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.project_member import Role
from app.models.tag import Tag
from app.models.task import Task
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.tag import TagRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskTreeResponse, TaskUpdate
from app.services.comment import CommentService
from app.services.tag import TagService
from app.services.task import TaskService

router = APIRouter(tags=["Задачи и Обсуждения"])

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
) -> Task:
    task_repository = TaskRepository(session=db)
    project_repository = ProjectRepository(session=db)
    user_repository = UserRepository(session=db)
    
    task_service = TaskService(
        task_repo=task_repository,
        project_repo=project_repository,
        user_repo=user_repository
    )
    
    return await task_service.create_task(project_id, data)

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> Task:
    task_repository = TaskRepository(session=db)
    task_service = TaskService(task_repository, None, None)
    
    return await task_service.get_task_by_id(task_id)

@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def get_project_tasks(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Task]:
    task_service = TaskService(TaskRepository(db), ProjectRepository(db), UserRepository(db))
    
    return await task_service.get_project_tasks(project_id, current_user.id)

@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Task:
    task_service = TaskService(TaskRepository(db), ProjectRepository(db), UserRepository(db))
    
    return await task_service.update_task_details(
        project_id=project_id,
        task_id=task_id,
        user_id=current_user.id,
        task_data=data
    )

@router.delete("/projects/{project_id}/tasks/{task_id}")
async def delete_task(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(CheckProjectRole([Role.OWNER, Role.MANAGER]))
):
    task_repository = TaskRepository(session=db)
    task_service = TaskService(task_repository, None, None)
    
    return await task_service.delete_task(task_id)

@router.post("/tags", response_model=TagResponse)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)) -> Tag:
    tag_repository = TagRepository(session=db)
    task_repository = TaskRepository(session=db)
    
    tag_service = TagService(
        tag_repo=tag_repository,
        task_repo=task_repository
    )
    
    return await tag_service.create_new_tag(tag_data=data)

@router.get("/tags", response_model=list[TagResponse])
async def get_all_tags(
    db: AsyncSession = Depends(get_db)
) -> list[Tag]:
    tag_service = TagService(TagRepository(db), TaskRepository(db))
    
    return await tag_service.get_all_tags()

@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    tag_service = TagService(TagRepository(db), TaskRepository(db))
    await tag_service.delete_tag_by_id(tag_id)
    
    return None

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

@router.get("/projects/{project_id}/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    project_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Comment]:
    comment_service = CommentService(
        CommentRepository(db),
        TaskRepository(db),
        UserRepository(db),
        ProjectRepository(db)
    )
    
    return await comment_service.get_task_comments(
        project_id=project_id,
        task_id=task_id,
        user_id=current_user.id
    )
    
@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    comment_service = CommentService(
        CommentRepository(db),
        TaskRepository(db),
        UserRepository(db)
    )

    await comment_service.delete_comment_by_id(comment_id, current_user.id)
    
    return None

@router.get("/projects/{project_id}/tasks/tree", response_model=list[TaskTreeResponse])
async def get_tasks_tree(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[TaskTreeResponse]:
    task_service = TaskService(TaskRepository(db), ProjectRepository(db))
    
    return await task_service.get_project_tasks_tree(project_id, current_user.id)
