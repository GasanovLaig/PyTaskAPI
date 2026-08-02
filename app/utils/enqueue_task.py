import structlog
from typing import Any
from arq import ArqRedis
from arq.jobs import Job

from app.core.exceptions import QueueServiceUnavailableError

logger = structlog.get_logger("infra.arq_worker")

async def enqueue_task(
    arq_pool: ArqRedis | None,
    task_name: str,
    suppress_errors: bool = True,
    **kwargs: Any
) -> Job | None:
    """Безопасно отправляет задачу в ARQ и возвращает объект Job, защищая основной поток выполнения."""
    if arq_pool is None:
        logger.warning("ARQ pool is not initialized, skipping task", task=task_name)
        if not suppress_errors:
            raise QueueServiceUnavailableError("Очередь задач ARQ не инициализирована")
        return None
    
    try:
        return await arq_pool.enqueue_job(task_name, **kwargs)
    except Exception as error:
        logger.error("Failed to enqueue job to ARQ", task=task_name, error=str(error))
        if not suppress_errors:
            raise QueueServiceUnavailableError(f"Сбой сервиса очередей: {error}")
        
        return None
