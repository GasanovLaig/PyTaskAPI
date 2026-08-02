from app.worker.tasks.analytics import log_activity_task
from app.worker.tasks.reports import generate_project_report_task
from app.worker.tasks.notifications import send_assignee_email_task

all_tasks = [
    log_activity_task,
    send_assignee_email_task,
    generate_project_report_task,
]

__all__ = ["all_tasks"]
