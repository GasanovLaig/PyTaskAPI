from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, async_session_factory, Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.tag import Tag
from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.tag import TagRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.services.comment import CommentService
from app.services.project import ProjectService
from app.services.tag import TagService
from app.services.task import TaskService

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def main():
    return {"message": "FastAPI successfully launched!"}

async def get_db():
    async with async_session_factory() as session:
        yield session

@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    user_repository = UserRepository(session=db)
    auth_service = AuthService(user_repo=user_repository)
    
    return await auth_service.register_new_user(user_data=user_data)

@app.post("/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, user_id:int, db: AsyncSession = Depends(get_db)) -> Project:
    user_repository = UserRepository(session=db)
    project_repository = ProjectRepository(session=db)
    project_service = ProjectService(project_repo=project_repository, user_repo=user_repository)
    
    return await project_service.create_new_project(user_id=user_id, project_data=project_data)

@app.get("/users/{user_id}/projects", response_model=list[ProjectResponse])
async def get_projects_by_user(user_id: int, db: AsyncSession = Depends(get_db)) -> list[Project]:
    user_repository = UserRepository(session=db)
    project_repository = ProjectRepository(session=db)
    project_service = ProjectService(user_repo=user_repository, project_repo=project_repository)
    
    return await project_service.get_projects_by_user(user_id=user_id)

@app.post("/projects/{project_id}/tasks", response_model=TaskResponse)
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
    
    return await task_service.create_task(project_id, data)

@app.post("/tags", response_model=TagResponse)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)) -> Tag:
    tag_repository = TagRepository(session=db)
    task_repository = TaskRepository(session=db)
    
    tag_service = TagService(
        tag_repo=tag_repository,
        task_repo=task_repository
    )
    
    return await tag_service.create_new_tag(tag_data=data)

@app.post("/tasks/{task_id}/tags/{tag_id}", response_model=TaskResponse)
async def create_task_tags(task_id: int, tag_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    tag_repository = TagRepository(session=db)
    task_repository = TaskRepository(session=db)
    
    tag_service = TagService(
        tag_repo=tag_repository,
        task_repo=task_repository
    )
    
    return await tag_service.attach_tag_to_task(task_id=task_id, tag_id=tag_id)

@app.post("/tasks/{task_id}/comments", response_model=CommentResponse)
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
