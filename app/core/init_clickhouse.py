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

async def init_clickhouse():
    """Автоматическая инициализация структуры данных ClickHouse при старте API."""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.CLICKHOUSE_URL,
                params={"query": CLICKHOUSE_DDL}
            )
            if response.status_code == 200:
                logger.info("ClickHouse schema initialized successfully")
            else:
                logger.info("ClickHouse init failed", error=response.text)
    except Exception as exception:
        logger.error("ClickHouse connection error", error=str(exception))
