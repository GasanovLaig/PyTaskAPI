from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, async_session_factory, Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.tag import Tag
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.user import UserCreate, UserResponse

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
    new_user = User(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@app.post("/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, user_id:int, db: AsyncSession = Depends(get_db)) -> Project:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    new_project = Project(
        title=project_data.title,
        description=project_data.description
    )
    new_project.users.append(user)
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return new_project

@app.get("/users/{user_id}/projects", response_model=list[ProjectResponse])
async def get_user_projects_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> list[Project]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    await db.refresh(user, ["projects"])
    return user.projects

@app.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db)
) -> Task:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Такого проекта не существует")
    
    if data.performer_id is not None:
        performer = await db.get(User, data.performer_id)
        if performer is None:
            raise HTTPException(status_code=404, detail="Такой испольнитель не найден")
    
    if data.parent_task_id == 0:
        data.parent_task_id = None

    if data.parent_task_id is not None:
        parent_task = await db.get(Task, data.parent_task_id)
        if parent_task is None:
            raise HTTPException(status_code=404, detail="Такая родительская задача не найдена")
        
        if parent_task.project_id != project_id:
            raise HTTPException(status_code=400, detail="Родительская задача не принадлежит тому же проекту")

    new_task = Task(
        title=data.title,
        description=data.description,
        project_id=project_id,
        performer_id=data.performer_id,
        parent_task_id=data.parent_task_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task, attribute_names=["tags", "subtasks"])

    return new_task

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
