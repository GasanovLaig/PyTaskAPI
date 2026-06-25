from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as project_router
from app.api.v1.tasks import router as task_router

app = FastAPI(title="PyTaskAPI")

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)
