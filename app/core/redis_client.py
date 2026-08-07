import structlog
import redis.asyncio as aioredis

from app.core.config import settings

logger = structlog.get_logger("infra.redis")
    
class RedisManager:
    def __init__(self):
        self.client: aioredis.Redis | None = None
        
    async def connect(self) -> aioredis.Redis:
        """Инициализация пула соединений при старте приложения."""
        if not self.client:
            logger.info("Connecting to Redis pool...")
            self.client = aioredis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=20,
                health_check_interval=30
            )
        
        return self.client
    
    async def disconnect(self) -> None:
        """Плавное закрытие пула при остановке приложения."""
        if self.client:
            logger.info("Disconnecting from Redis pool...")
            await self.client.close()
            self.client = None

redis_manager = RedisManager()
