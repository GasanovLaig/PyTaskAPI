import uuid
import json
from httpx import AsyncClient
from datetime import datetime, timezone

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
    """Нативный асинхронный воркер отправки логов в ClickHouse."""
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
        
    if current_size >= BATCH_SIZE_LIMIT:
        await flush_logs(ctx, reason="batch_size_limit")
        
async def flush_logs(ctx, reason: str):
    """Вспомогательная функция отправки накопленной пачки логов в ClickHouse."""
    async with ctx["logs_lock"]:
        if not ctx["logs_batch"]:
            return
        
        to_send = list(ctx["logs_batch"])
        ctx["logs_batch"].clear()
        
    client: AsyncClient = ctx["http_client"]
    CLICKHOUSE_URL = ctx["clickhouse_url"]
    
    ndjson_data = "\n".join(json.dumps(log) for log in to_send) + "\n"
    try:
        response = await client.post(
            CLICKHOUSE_URL,
            params={"query": "INSERT INTO default.activity_logs FORMAT JSONEachRow"},
            content=ndjson_data,
            headers={"Content-Type": "application/x-ndjson"}
        )
        if response.status_code != 200:
            print(f"ClickHouse Batch Error: {response.text}")
            response.raise_for_status()
        else:
            print(f"DEBUG: Успешно отправлена пачка из {len(to_send)} логов в ClickHouse (триггер: {reason}).")
    except Exception as error:
        print(f"DEBUG: Ошибка отправки пачки в ClickHouse: {type(error).__name__} -> {error}")
        
        async with ctx["logs_lock"]:
            ctx["logs_batch"].extend(to_send)
            
        raise error
        