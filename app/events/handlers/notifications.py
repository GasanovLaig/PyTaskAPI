from arq.connections import ArqRedis

from app.utils.enqueue_task import enqueue_task
from app.events.events import TaskCreatedEvent, TaskUpdatedEvent

class NotificationHandler:
    """Хендлер для отправки асинхронных email-уведомлений через SMTP воркер."""
    def __init__(self, arq_pool: ArqRedis):
        self.arq_pool = arq_pool

    async def on_task_created(self, event: TaskCreatedEvent):
        if event.performer_id is None:
            return
            
        email = event.notify_metadata.get("performer_email")
        project_title = event.notify_metadata.get("project_title")
        
        if email:
            await enqueue_task(
                self.arq_pool, "send_assignee_email_task",
                performer_email=email, task_title=event.task_title, project_title=project_title
            )

    async def on_task_updated(self, event: TaskUpdatedEvent):
        db_data, old, new = event.db_data, event.old_metadata, event.new_metadata
        
        if "performer_id" in db_data and new["performer_id"] != old["performer_id"]:
            if new["performer_id"] is not None:
                email = event.notify_metadata.get("performer_email")
                project_title = event.notify_metadata.get("project_title")
                
                if email:
                    await enqueue_task(
                        self.arq_pool, "send_assignee_email_task",
                        performer_email=email, task_title=new["title"], project_title=project_title
                    )
        
                    