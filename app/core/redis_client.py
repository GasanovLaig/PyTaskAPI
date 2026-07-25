from typing import AsyncGenerator
import redis.asyncio as aioredis

from app.core.config import settings

_redis_client: aioredis.Redis | None = None

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    yield _redis_client
