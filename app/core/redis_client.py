import redis.asyncio as aioredis
from app.core.config import settings

redis_client = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)

async def get_redis():
    yield redis_client
