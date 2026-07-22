from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.tags import router as tags_router
from app.api.v1.comments import router as comments_router
from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import structlog_middleware
from app.core.logger import setup_logger

setup_logger()

app = FastAPI(title="PyTaskAPI")

@app.middleware("http")
async def add_structlog_middleware(request, call_next):
    return await structlog_middleware(request, call_next)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(comments_router)

register_exception_handlers(app)
