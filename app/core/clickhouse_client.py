import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger("infra.clickhouse")

CLICKHOUSE_DDL = """
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID,
    user_id Nullable(Int64),
    project_id Int64,
    action LowCardinality(String),
    resource_type LowCardinality(String),
    resource_id Nullable(Int64),
    details Map(String, String),
    created_at DateTime64(3, 'UTC'),
    INDEX idx_project_id project_id TYPE minmax GRANULARITY 1
)
    ENGINE = MergeTree()
    ORDER BY(created_at, project_id, action)
    
    TTL created_at + INTERVAL 90 DAY
    SETTINGS index_granularity = 8192;
"""

logger = structlog.get_logger("infra.clickhouse")

class ClickHouseManager:
    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        
    async def connect(self) -> httpx.AsyncClient:
        """Инициализация постоянного пула HTTP-соединений."""
        if not self.client:
            logger.info("Initializing ClickHouse HTTP client pool...")
            
        limits = httpx.Limits(
            max_connections=50,
            max_keepalive_connections=20,
            keepalive_expiry=60.0
        )
        
        self.client = httpx.AsyncClient(
            base_url=settings.CLICKHOUSE_URL,
            limits=limits,
            timeout=httpx.Timeout(10.0)
        )
        
        await self._init_db_structure()
        
        return self.client
    
    async def _init_db_structure(self) -> None:
        """Скрытый внутренний метод для выполнения миграций / DDL."""
        logger.info("Checking and initializing ClickHouse database schema...")
        try:
            response = await self.client.post("/", params={"query": CLICKHOUSE_DDL})
            response.raise_for_status()
            logger.info("ClickHouse database schema is up to date")
        except Exception as error:
            logger.error("ClickHouse schema initialization failed", error=str(error))
            raise error
    
    async def disconnect(self) -> None:
        """Плавное закрытие пула при выключении."""
        if self.client:
            logger.info("Closing ClickHouse HTTP client pool...")
            await self.client.aclose()
            self.client = None
            
clickhouse_manager = ClickHouseManager()
