from fastapi import Request
import redis.asyncio as aioredis

async def get_redis(request: Request) -> aioredis.Redis:
    """Зависимость для роутеров FastAPI.
    Быстро возвращает готовый пул сокетов.
    """
    return request.app.state.redis
