from typing import TYPE_CHECKING
from sqlalchemy import Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.project_member import project_members_table
if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    projects: Mapped[list["Project"]] = relationship(secondary=project_members_table, back_populates="users")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user")
