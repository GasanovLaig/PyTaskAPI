import redis.asyncio as aioredis
from arq.connections import ArqRedis
from app.core.events import event_bus

from app.events.events import (
    TaskCreatedEvent, TaskUpdatedEvent, TaskDeletedEvent,
    UserRegisteredEvent, AuthFailedEvent, AuthLoginEvent,
    ProjectCreatedEvent, ProjectMemberAddedEvent, ProjectUpdatedEvent,ProjectDeletedEvent,
    TagCacheInvalidationEvent
)
from app.events.handlers import ActivityLogHandler, CacheInvalidationHandler, NotificationHandler

def configure_event_bus(arq_pool: ArqRedis, redis_client: aioredis.Redis):
    """Сборка EDA конструктора приложения."""
    
    logger_handler = ActivityLogHandler(arq_pool=arq_pool)
    cache_handler = CacheInvalidationHandler(redis_client=redis_client)
    notify_handler = NotificationHandler(arq_pool=arq_pool)
    
    event_bus.register(TaskCreatedEvent, logger_handler.on_task_created)
    event_bus.register(TaskUpdatedEvent, logger_handler.on_task_updated)
    event_bus.register(TaskDeletedEvent, logger_handler.on_task_deleted)
    event_bus.register(UserRegisteredEvent, logger_handler.on_user_registered)
    event_bus.register(AuthFailedEvent, logger_handler.on_auth_failed)
    event_bus.register(AuthLoginEvent, logger_handler.on_auth_login)
    event_bus.register(ProjectCreatedEvent, logger_handler.on_project_created)
    event_bus.register(ProjectMemberAddedEvent, logger_handler.on_project_member_added)
    event_bus.register(ProjectUpdatedEvent, logger_handler.on_project_updated)
    event_bus.register(ProjectDeletedEvent, logger_handler.on_project_deleted)
    
    event_bus.register(TaskCreatedEvent, cache_handler.__call__)
    event_bus.register(TaskUpdatedEvent, cache_handler.__call__)
    event_bus.register(TaskDeletedEvent, cache_handler.__call__)
    event_bus.register(TagCacheInvalidationEvent, cache_handler.__call__)
    
    event_bus.register(TaskCreatedEvent, notify_handler.on_task_created)
    event_bus.register(TaskUpdatedEvent, notify_handler.on_task_updated)
