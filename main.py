from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_engine, async_session_factory, Base
from app.models import User, Project
from app.schemas.project import ProjectCreate, ProjectResponse
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
