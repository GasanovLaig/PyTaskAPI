from typing import Any
import redis.asyncio as aioredis

from app.utils.clear_cache_key import clear_cache_key

class CacheInvalidationHandler:
    """Хендлер для очистки инвалидации кэша дерева задач в Redis."""
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    async def __call__(self, event: Any):
        await clear_cache_key(self.redis_client, f"project:{event.project_id}:tasks_tree")
        