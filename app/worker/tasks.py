import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.worker.celery_app import celery_app
from app.core.config import settings

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
    # Имитируем тяжелые расчеты (например, 5 секунд)
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
