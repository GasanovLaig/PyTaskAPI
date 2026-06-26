from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User

class Role(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    DEVELOPER = "developer"

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, name="role"), nullable=False, default=Role.DEVELOPER)
    
    user: Mapped["User"] = relationship(back_populates="project_memberships")
    project: Mapped["Project"] = relationship(back_populates="memberships")
