import structlog
from arq import create_pool
from fastapi import Request
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings
    
logger = structlog.get_logger("infra.arq")

class ArqManager:
    def __init__(self):
        self.arq_pool: ArqRedis | None = None
        
    async def connect(self) -> ArqRedis:
        """Инициализация пула задач при старте."""
        if not self.arq_pool:
            logger.info("Connecting to ARQ Task Queue pool...")
            self.arq_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
            
        return self.arq_pool
    
    async def disconnect(self) -> None:
        """Закрытие пула задач при остановке."""
        if self.arq_pool:
            logger.info("Disconnecting from ARQ Task Queue pool...")
            await self.arq_pool.aclose()
            self.arq_pool = None
            
arq_manager = ArqManager()

async def get_arq_pool(request: Request) -> ArqRedis:
    """Мгновенно отдает пул из state приложения."""
    return request.app.state.arq_pool
