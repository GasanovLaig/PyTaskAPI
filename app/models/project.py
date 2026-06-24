from typing import TYPE_CHECKING
from sqlalchemy import Identity, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.project_member import project_members_table
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str |  None] = mapped_column(Text, nullable=True)

    users: Mapped[list["User"]] = relationship(secondary=project_members_table, back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project")
