import structlog
from typing import Any
from arq import ArqRedis

logger = structlog.get_logger("infra.arq_worker")

async def enqueue_task(arq_pool: ArqRedis | None, task_name: str, **kwargs: Any) -> None:
    """Безопасно отправляет задачу в ARQ, защищая основной поток выполнения."""
    if arq_pool is None:
        logger.warning("ARQ pool is not initialized, skipping task", task=task_name)
        return
    
    try:
        await arq_pool.enqueue_job(task_name, **kwargs)
    except Exception as error:
        logger.error("Failed to enqueue job to ARQ", task=task_name, error=str(error))
