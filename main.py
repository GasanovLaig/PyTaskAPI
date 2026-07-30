import structlog
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.tags import router as tags_router
from app.api.v1.comments import router as comments_router
from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import structlog_middleware
from app.api.dependencies.arq import get_arq_pool
from app.core.logger import setup_logger
from app.core.init_clickhouse import init_clickhouse

logger = structlog.get_logger("app.lifespan")
setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    await init_clickhouse()
    arq_pool = await get_arq_pool()
    logger.info("Infrastructure connections established")
    
    yield
    
    logger.info("Application shutdown initiated")
    await arq_pool.close()
    logger.info("Infrastructure connections closed")

app = FastAPI(title="PyTaskAPI", lifespan=lifespan)

@app.middleware("http")
async def add_structlog_middleware(request, call_next):
    return await structlog_middleware(request, call_next)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(comments_router)

register_exception_handlers(app)
