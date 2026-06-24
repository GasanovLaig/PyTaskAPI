from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Identity, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.project import Project
from app.models.user import User
if TYPE_CHECKING:
    from app.models.tag import Tag
from app.models.task_tags import task_tags_table

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)

    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    
    performer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user: Mapped["User | None"] = relationship("User", back_populates="tasks")
    
    parent_task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    parent_task: Mapped["Task | None"] = relationship("Task", back_populates="subtasks", remote_side=[id])
    subtasks: Mapped[list["Task"]] = relationship("Task", back_populates="parent_task")

    tags: Mapped[list["Tag"]] = relationship(secondary=task_tags_table, back_populates="tasks")
