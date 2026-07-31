import asyncio
from httpx import AsyncClient, Limits
from arq.connections import RedisSettings

from app.core.config import settings
from app.worker.arq_tasks import flush_logs, log_activity_task

async def flush_timer_loop(ctx):
    """Фоновая задача, которая проверяет буфер каждые 5 секунд 
    и сбрасывает логи, если они там залежались."""
    try:
        while True:
            await asyncio.sleep(5)
            await flush_logs(ctx, reason="timeout")
    except asyncio.CancelledError:
        pass

async def startup(ctx):
    ctx["http_client"] = AsyncClient(
        limits=Limits(max_connections=100, max_keepalive_connections=20)
    )
    ctx["clickhouse_url"] = settings.CLICKHOUSE_URL
    
    ctx["logs_batch"] = []
    ctx["logs_lock"] = asyncio.Lock()
    ctx["flush_timer"] = asyncio.create_task(flush_timer_loop(ctx))

async def shutdown(ctx):
    if "flush_timer" in ctx:
        ctx["flush_timer"].cancel()
        
    await flush_logs(ctx, reason="worker_shutdown")
    
    client: AsyncClient = ctx.get("http_client")
    if client:
        await client.aclose()
    
class WorkerSettings:
    functions = [log_activity_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    