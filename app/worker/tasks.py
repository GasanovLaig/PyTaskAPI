import time
import uuid
import httpx
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
from arq.connections import RedisSettings
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.worker.celery_app import celery_app

@celery_app.task(name="tasks.send_assignee_email")
def send_assignee_email(performer_email: str, task_title: str, project_title: str):
    """Фоновая задача Celery для отправки SMTP-уведомления на Mailhog."""
    
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.MAIL_SENDER_EMAIL
        msg["To"] = performer_email
        msg["Subject"] = f"Новая задача в проекте: {project_title}"
        
        body = f"""
        Приветствуем!
        
        Вы были назначены исполнителем новой задачи в корпоративном трекере задач PyTaskAPI.
        
        Проект: {project_title}
        Задача: {task_title}
        
        Пожалуйста, ознакомьтесь с деталями задачи в вашем рабочем пространстве.
        """
        
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        with smtplib.SMTP(settings.MAIL_SMTP_HOST, settings.MAIL_SMTP_PORT) as server:
            server.sendmail(settings.MAIL_SENDER_EMAIL, performer_email, msg.as_string())
            
        print(f"[Celery] Письмо по задаче '{task_title}' успешно доставлено на Mailhog!")
        
        return f"Email successfully sent to {performer_email}"
    
    except Exception as error:
        print(f"[Celery] Ошибка отправки письма: {str(error)}")
        
        return f"Failed to send email: {str(error)}"

@celery_app.task(name="tasks.generate_project_report")
def generate_project_report(project_id: int):
    """Тяжелая фоновая задача генерации агрегированной статистики по проекту."""
    
    print(f"[Celery] Запущена генерация отчета для проекта ID {project_id}...")
    time.sleep(5)
    
    report_result = {
        "project_id": project_id,
        "total_tasks": 42,
        "completed_tasks": 30,
        "efficiency_rate": "71.4%",
        "status": "Generated successfully"
    }
    
    print(f"[Celery] Отчет для проекта {project_id} готов!")
    
    return report_result

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
    
    CLICKHOUSE_URL = "http://127.0.0.1:8123"
    stringfield_details = {k: str(v) for k, v in details.items()} if details else {}
    now_utc = datetime.now(timezone.utc)
    formatted_date = now_utc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                CLICKHOUSE_URL,
                params={"query": "INSERT INTO default.activity_logs FORMAT JSONEachRow"},
                json={
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "project_id": project_id if project_id is not None else 0,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": stringfield_details,
                    "created_at": formatted_date
                }
            )
        
            if response.status_code != 200:
                print(f"ClickHouse Error: {response.text}")
                response.raise_for_status()
        except Exception as error:
            print(f"DEBUG: Критическая ошибка при подключении к {CLICKHOUSE_URL}: {type(error).__name__} -> {error}")
            raise error

async def startup(ctx):
    pass

async def shutdown(ctx):
    pass

class WorkerSettings:
    functions = [log_activity_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
