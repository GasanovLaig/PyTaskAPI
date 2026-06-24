from sqlalchemy import ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.task import Task
from app.models.user import User

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, Identity(always=True), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    parent_comment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), default=None)
    
    parent_comment: Mapped["Comment | None"] = relationship("Comment", remote_side=[id], back_populates="subcomments")
    subcomments: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent_comment")

    author: Mapped["User"] = relationship("User", back_populates="comments")
    task: Mapped["Task"] = relationship("Task", back_populates="comments")
