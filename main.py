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
from app.core.logger import setup_logger
from app.core.redis_client import redis_manager
from app.api.dependencies.arq import arq_manager

logger = structlog.get_logger("app.lifespan")
setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== STARTUP: Initializing infrastructure pools ===")
    app.state.redis = await redis_manager.connect()
    app.state.arq_pool = await arq_manager.connect()
    logger.info("=== STARTUP: Infrastructure is fully ready ===")
    
    yield
    
    logger.info("=== SHUTDOWN: Closing infrastructure pools ===")
    await redis_manager.disconnect()
    await arq_manager.disconnect()
    logger.info("=== SHUTDOWN: All connections safely closed ===")

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
