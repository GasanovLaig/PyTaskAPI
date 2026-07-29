from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings

_arq_pool: ArqRedis | None = None

async def get_arq_pool() -> ArqRedis:
    global _arq_pool
    if _arq_pool is None:
        REDIS_SETTINGS = RedisSettings.from_dsn(settings.REDIS_URL)
        _arq_pool = await create_pool(REDIS_SETTINGS)
        
    return _arq_pool