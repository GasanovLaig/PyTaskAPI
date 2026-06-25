from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, async_session_factory, Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.tag import Tag
from app.models.comment import Comment
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.services.project import ProjectService
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
    result = await db.execute(text("SELECT id FROM tags WHERE name=:tag_name"), {"tag_name": data.name})
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Тег с таким названием уже существует")
    
    new_tag = Tag(
        name=data.name
    )
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)

    return new_tag

@app.post("/tasks/{task_id}/tags/{tag_id}", response_model=TaskResponse)
async def create_task_tags(task_id: int, tag_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Такой задачи не существует")
    
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Такого тега не существует")
    
    await db.refresh(task, ["tags"])

    if tag not in task.tags:
        task.tags.append(tag)

    await db.commit()
    await db.refresh(task, attribute_names=["tags"])

    return task

@app.post("/tasks/{task_id}/comments", response_model=CommentResponse)
async def create_comment(task_id: int, data: CommentCreate, db: AsyncSession = Depends(get_db)) -> Comment:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Задача с ID {task_id} не найдена")
    
    author = await db.get(User, data.author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Автор с таким ID не найден")

    if data.parent_comment_id == 0:
        data.parent_comment_id = None

    if data.parent_comment_id is not None:
        parent_comment = await db.get(Comment, data.parent_comment_id)
        if parent_comment is None:
            raise HTTPException(status_code=404, detail="Родительский комментарий с таким ID не найден")
        
        if parent_comment.task_id != task_id:
            raise HTTPException(status_code=400, detail="Родительский комментарий принадлежит к другой задаче")

    new_comment = Comment(
        text=data.text,
        task_id=task_id,
        author_id=data.author_id,
        parent_comment_id=data.parent_comment_id
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    return new_comment
