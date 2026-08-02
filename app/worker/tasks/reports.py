import asyncio
import structlog

logger = structlog.get_logger("infra.arq_worker")

async def generate_project_report_task(ctx, project_id: int):
    """Тяжелая фоновая задача генерации агрегированной статистики по проекту (Заглушка)."""
    job_id = ctx.get("job_id", "report_coroutine")
    logger.info("project_report_generation_started", project_id=project_id, job_id=job_id)
    
    await asyncio.sleep(5)
    
    report_result = {
        "project_id": project_id,
        "total_tasks": 42,
        "completed_tasks": 30,
        "efficiency_rate": "71.4%",
        "status": "Generated successfully"
    }
    
    logger.info("project_report_generation_completed", project_id=project_id, job_id=job_id)
    
    return report_result
