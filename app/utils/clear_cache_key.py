import structlog
from redis.asyncio import Redis

logger = structlog.get_logger("infra.cache")

async def clear_cache_key(redis_client: Redis | None, key: str) -> None:
    """Безопасно удаляет ключ из Redis, защищая основной поток от сбоев."""
    if redis_client is None:
        logger.warning("Redis client is not initialized, skipping deletion.", key=key)
        return
    try:
        await redis_client.delete(key)
    except Exception as error:
        logger.error("Failed to delete key from Redis.", key=key, error=str(error))
