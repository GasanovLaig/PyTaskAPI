from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base

task_tags_table = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)
