import uuid
import json
import structlog
from httpx import AsyncClient
from datetime import datetime, timezone

logger = structlog.get_logger("infra.arq_worker")

BATCH_SIZE_LIMIT = 1000

async def log_activity_task(
    ctx,
    user_id: int | None,
    project_id: int | None,
    action: str,
    resource_type: str,
    resource_id: int | None,
    details: dict | None
):
    """Буферизация логирования. Собирает логи в пачки для отправки в БД."""
    stringfield_details = {key: str(value) for key, value in details.items()} if details else {}
    formatted_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    log_entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "project_id": project_id if project_id is not None else 0,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": stringfield_details,
        "created_at": formatted_date
    }
    
    async with ctx["logs_lock"]:
        ctx["logs_batch"].append(log_entry)
        current_size = len(ctx["logs_batch"])
        
    job_id = ctx.get("job_id", "unknown_job")
    logger.debug(
        "activity_received_for_buffer",
        job_id=job_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id
    )
    if current_size >= BATCH_SIZE_LIMIT:
        logger.info("buffer_limit_reached", current_size=current_size, limit=BATCH_SIZE_LIMIT, job_id=job_id)
        await flush_logs(ctx, reason="batch_size_limit")
        
async def flush_logs(ctx, reason: str):
    """Функция отправки накопленной пачки логов в ClickHouse."""
    async with ctx["logs_lock"]:
        if not ctx["logs_batch"]:
            return
        
        to_send = list(ctx["logs_batch"])
        ctx["logs_batch"].clear()
        
    client: AsyncClient = ctx["http_client"]
    CLICKHOUSE_URL = ctx["clickhouse_url"]
    
    ndjson_data = "\n".join(json.dumps(log) for log in to_send) + "\n"
    job_id = logger.get("job_id", "flush_coroutine")
    logger.info("sending_batch_to_clickhouse", batch_size=len(to_send), reason=reason, job_id=job_id)
    try:
        response = await client.post(
            CLICKHOUSE_URL,
            params={"query": "INSERT INTO default.activity_logs FORMAT JSONEachRow"},
            content=ndjson_data,
            headers={"Content-Type": "application/x-ndjson"}
        )
        if response.status_code != 200:
            logger.error("clickhouse_batch_rejected", status_code=response.status_code, error=response.text, job_id=job_id)
            response.raise_for_status()
        else:
            logger.info("batch_successfully_written", batch_size=len(to_send), reason=reason, job_id=job_id)
    except Exception as error:
        logger.exception("clickhouse_send_failed", reason=reason, job_id=job_id)
        
        async with ctx["logs_lock"]:
            ctx["logs_batch"].extend(to_send)
            
        raise error
        