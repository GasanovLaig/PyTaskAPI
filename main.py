from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, async_session_factory, Base
from app.models import User, Project, Task
from app.schemas.project import ProjectCreate, ProjectResponse
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
    
    performer = await db.get(User, data.performer_id)
    if data.performer is None:
        raise HTTPException(status_code=404, detail="Такого пользователя не существует")
    
    if data.parent_task_id is not None:
        parent_task = await db.get(Task ,data.parent_task_id)
        if parent_task is None:
            raise HTTPException(status_code=404, detail="Такой родительской задачи не существует")
        
        if parent_task.project_id != project_id:
            raise HTTPException(status_code=400, detail="Родительская задача не принадлежит тому же проекту")

    new_task = Task(
        title=data.title,
        description=data.description,
        project_id=project_id,
        performer_id=data.performer_id,
        parent_id=data.parent_task_id,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task
