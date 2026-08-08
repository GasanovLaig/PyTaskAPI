from arq.connections import ArqRedis

from app.utils.enqueue_task import enqueue_task
from app.events.events import (
    TaskCreatedEvent, TaskUpdatedEvent, TaskDeletedEvent,
    UserRegisteredEvent, AuthFailedEvent, AuthLoginEvent,
    ProjectCreatedEvent, ProjectMemberAddedEvent, ProjectUpdatedEvent, ProjectDeletedEvent
)

class ActivityLogHandler:
    """Хендлер для асинхронного буферизованного логирования всех действий в ClickHouse."""
    def __init__(self, arq_pool: ArqRedis):
        self.arq_pool = arq_pool

    async def on_task_created(self, event: TaskCreatedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="task.created", resource_type="Task", resource_id=event.task_id,
            details={"task_title": event.task_title, "status": event.task_status}
        )

    async def on_task_updated(self, event: TaskUpdatedEvent):
        history_details = {}
        db_data, old, new = event.db_data, event.old_metadata, event.new_metadata
        
        if "title" in db_data and new["title"] != old["title"]:
            history_details["old_title"] = old["title"]
            history_details["new_title"] = new["title"]
        if "status" in db_data and new["status"] != old["status"]:
            history_details["old_status"] = old["status"]
            history_details["new_status"] = new["status"]
        if "performer_id" in db_data and new["performer_id"] != old["performer_id"]:
            history_details["old_performer_id"] = old["performer_id"]
            history_details["new_performer_id"] = new["performer_id"]

        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="task.updated", resource_type="Task", resource_id=event.task_id,
            details=history_details
        )

    async def on_task_deleted(self, event: TaskDeletedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="task.deleted", resource_type="Task", resource_id=event.task_id,
            details=None
        )

    async def on_user_registered(self, event: UserRegisteredEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.user_id, project_id=None,
            action="user.registered", resource_type="User", resource_id=event.user_id,
            details={"email": event.email}
        )

    async def on_auth_failed(self, event: AuthFailedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=None, project_id=None,
            action="auth.failed", resource_type="User", resource_id=None,
            details={"attempted_email": event.attempted_email}
        )

    async def on_auth_login(self, event: AuthLoginEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.user_id, project_id=None,
            action="auth.login", resource_type="User", resource_id=event.user_id,
            details=None
        )

    async def on_project_created(self, event: ProjectCreatedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="project.created", resource_type="Project", resource_id=event.project_id,
            details={"project_title": event.project_title}
        )

    async def on_project_member_added(self, event: ProjectMemberAddedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="project.member_added", resource_type="User", resource_id=event.user_id,
            details={"role": event.role}
        )

    async def on_project_updated(self, event: ProjectUpdatedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="project.updated", resource_type="Project", resource_id=event.project_id,
            details={"updated_fields": event.updated_fields}
        )

    async def on_project_deleted(self, event: ProjectDeletedEvent):
        await enqueue_task(
            self.arq_pool, "log_activity_task",
            user_id=event.current_user_id, project_id=event.project_id,
            action="project.deleted", resource_type="Project", resource_id=event.project_id,
            details=None
        )
