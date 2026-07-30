import uuid
from datetime import datetime, timezone

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
    datetime_now_utc_iso = datetime.now(timezone.utc).isoformat()
    
    client = ctx["http_client"]
    CLICKHOUSE_URL = ctx["clickhouse_url"]
    try:
        response = await client.post(
            CLICKHOUSE_URL,
            params={"query": "INSERT INTO default.activity_logs FORMAT JSONEachRow"},
            json={
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "project_id": project_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": stringfield_details,
                "created_at": datetime_now_utc_iso
            }
        )
    
        if response.status_code != 200:
            print(f"ClickHouse Error: {response.text}")
            response.raise_for_status()
    except Exception as error:
        print(f"DEBUG: Критическая ошибка при подключении к {CLICKHOUSE_URL}: {type(error).__name__} -> {error}")
        raise error
        