import structlog
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

class Base(DeclarativeBase):
    pass

logger = structlog.get_logger("infra.postgres")

class DatabaseManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        
    async def connect(self) -> async_sessionmaker[AsyncSession]:
        if not self.engine:
            logger.info("postgres_client_pool_initializing")
            
            self.engine = create_async_engine(
                settings.DATABASE_URL_ASYNC,
                echo=False,                      # В проде echo=True забьет все логи гигабайтами SQL
                pool_size=15,                    # Держим 15 готовых сокетов всегда открытыми
                max_overflow=5,                  # В пиках разрешаем доращивать пул еще на 5 сокетов
                pool_timeout=30,                 # Ждем свободный сокет не более 30 сек (защита от зависания роутов)
                pool_recycle=1800,               # Сбрасывать сокет каждые 30 минут (защита от обрывов со стороны СУБД)
                pool_pre_ping=True               # Проверять живость сокета перед выдачей в UOW (авто-реконнект)
            )
            
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            
            await self._pre_warm_pool()
            
        return self.session_factory
            
    async def _pre_warm_pool(self) -> None:
        """Отправляет тестовый пинг в БД для прогрева пула сокетов."""
        logger.info("postgres_pool_pre_warming_started")
        try:
            async with self.session_factory() as session:
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
            logger.info("postgres_pool_pre_warming_completed")
        except Exception as error:
            logger.error("postgres_pool_pre_warming_failed", error=str(error))
            raise error
        
    async def disconnect(self) -> None:
        if self.engine:
            logger.info("postgres_client_pool_closing")
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
            logger.info("postgres_client_pool_closed_safely")
            
db_manager = DatabaseManager()
