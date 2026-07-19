from celery import Celery

from app.core.config import settings

REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "pytaskapi_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True
)
