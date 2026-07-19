import time

from app.worker.celery_app import celery_app

@celery_app.task(name="tasks.send_assignee_email")
def send_assignee_email(email: str, task_title: str):
    """Фоновая задача для отправки SMTP уведомления сотруднику."""
    
    print(f"[Celery] Начинаю отправку письма на {email}...")
    # Имитируем сетевую задержку отправки почты
    time.sleep(2)
    print(f"[Celery] Письмо по задаче '{task_title}' успешно отправлено!")
    
    return f"Email sent to {email}"

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
