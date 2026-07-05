from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.tag import Tag
    from app.models.comment import Comment
from app.models.task_tags import task_tags_table

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, native_enum=True, name="task_status"),
        default=TaskStatus.TODO
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    performer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    parent_task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)

    parent_task: Mapped["Task | None"] = relationship(
        "Task",
        back_populates="subtasks",
        remote_side=[id]
    )
    subtasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="parent_task",
        cascade="all, delete-orphan"
    )

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    performer: Mapped["User | None"] = relationship("User", back_populates="tasks")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=task_tags_table,
        back_populates="tasks"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="task",
        cascade="all, delete-orphan"
    )
