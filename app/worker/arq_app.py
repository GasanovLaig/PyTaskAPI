from httpx import AsyncClient, Limits
from arq.connections import RedisSettings

from app.worker.arq_tasks import log_activity_task
from app.core.config import settings

async def startup(ctx):
    ctx["http_client"] = AsyncClient(
        limits=Limits(max_connections=100, max_keepalive_connections=20)
    )
    ctx["clickhouse_url"] = settings.CLICKHOUSE_URL

async def shutdown(ctx):
    client: AsyncClient = ctx.get("http_client")
    if client:
        await client.aclose()
    
class WorkerSettings:
    functions = [log_activity_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    