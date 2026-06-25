from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import async_engine, Base
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as project_router
from app.api.v1.tasks import router as task_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="PyTaskAPI", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)

@app.get("/")
def main():
    return {"message": "FastAPI successfully launched!"}
