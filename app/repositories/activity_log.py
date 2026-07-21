from app.models.activity_log import ActivityLog
from app.repositories.base import BaseRepository

class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self, session):
        super().__init__(model=ActivityLog, session=session)
