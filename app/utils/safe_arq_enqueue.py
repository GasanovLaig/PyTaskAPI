import structlog

logger = structlog.get_logger("infra.arq")

async def safe_arq_enqueue(arq_pool, task_name: str, **kwargs):
    """Безопасно отправляет задачу в ARQ, защищая основной поток выполнения."""
    if arq_pool is None:
        logger.warning("ARQ pool is not initialized, skipping task", task=task_name)
        
        return None
    
    try:
        return await arq_pool.enqueue_job(task_name, **kwargs)
    except Exception as error:
        logger.error("Failed to enqueue job to ARQ", task=task_name, error=str(error))
        
        return None
