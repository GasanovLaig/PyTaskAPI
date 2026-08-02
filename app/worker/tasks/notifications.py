import structlog
import aiosmtplib
from email.message import EmailMessage

from app.core.config import settings

logger = structlog.get_logger("infra.arq_worker")

async def send_assignee_email_task(ctx, performer_email: str, task_title: str, project_title: str) -> None:
    """Фоновая задача ARQ для асинхронной отправки SMTP-уведомления на Mailhog."""
    job_id = ctx.get("job_id", "email_coroutine")
    
    message = EmailMessage()
    message["From"] = settings.MAIL_SENDER_EMAIL
    message["To"] = performer_email
    message["Subject"] = f"Новая задача в проекте: {project_title}"
    
    text = (
        f"Приветствуем!\n"
        f"Вы были назначены исполнителем новой задачи в PyTaskAPI.\n\n"
        f"Проект: {project_title}\n"
        f"Задача: {task_title}\n\n"
        f"Пожалуйста, ознакомьтесь с деталями в рабочем пространстве."
    )
    message.set_content(text)
    
    logger.info("attempting_to_send_email", performer_email=performer_email, task_title=task_title, job_id=job_id)
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_SMTP_HOST,
            port=settings.MAIL_SMTP_PORT
        )
        logger.info("email_successfully_sent", performer_email=performer_email, job_id=job_id)
    except Exception as error:
        logger.error("email_sending_failed", performer_email, error=str(error), job_id=job_id)
    