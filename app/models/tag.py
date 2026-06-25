from typing import TYPE_CHECKING
from sqlalchemy import Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
if TYPE_CHECKING:
    from app.models.task import Task
from app.models.task_tags import task_tags_table

class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    tasks: Mapped[list["Task"]] = relationship(secondary=task_tags_table, back_populates="tags")
