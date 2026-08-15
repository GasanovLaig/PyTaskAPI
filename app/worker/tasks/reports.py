import structlog

from app.repositories.task import TaskRepository

logger = structlog.get_logger("infra.arq_worker")

async def generate_project_report_task(ctx, project_id: int):
    """Тяжелая фоновая задача генерации агрегированной статистики по проекту (Заглушка)."""
    job_id = ctx.get("job_id", "report_coroutine")
    logger.info("project_report_generation_started", project_id=project_id, job_id=job_id)
    
    session_factory = ctx["db_session_factory"]
    async with session_factory() as session:
        try:
            task_repository = TaskRepository(session)
            analytics = await task_repository.get_project_analytics_data(project_id)
            logger.info("project_report_generation_completed", project_id=project_id, job_id=job_id)
            
            return {
                "project_id": project_id,
                "total_tasks": analytics["total_tasks"],
                "completed_tasks": analytics["completed_tasks"],
                "efficiency_rate": analytics["efficiency_rate"],
                "status_breakdown": analytics["status_breakdown"],
                "status": "Generated successfully"
            }
    
        except Exception as error:
            logger.error("project_report_generation_failed", project_id=project_id, error=str(error), job_id=job_id)
            return {
                "project_id": project_id,
                "status": "Failed",
                "error": str(error)
            }
            