from typing import TYPE_CHECKING
from sqlalchemy import Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.project_member import ProjectMember
    from app.models.tag import Tag

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    memberships: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="project",
        cascade="all, delete-orphan"
    )
