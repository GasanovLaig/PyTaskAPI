from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Identity, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.project import Project
from app.models.task_tags import task_tags_table

class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    
    __table_args__ = (
        Index("uq_idx_tag_name_project_id", "name", "project_id", unique=True),
    )
    
    project: Mapped["Project"] = relationship("Project", back_populates="tags")
    tasks: Mapped[list["Task"]] = relationship(
        secondary=task_tags_table,
        back_populates="tags"
    )
