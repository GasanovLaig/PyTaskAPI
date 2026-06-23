from enum import Enum
from sqlalchemy import Enum as SQLEnum, Column, ForeignKey, Integer, Table

from app.core.database import Base

class Role(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    DEVELOPER = "developer"

# from sqlalchemy.orm import Mapped, mapped_column
# class ProjectMember(Base):
#     __tablename__ = "project_members"
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
#     project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
#     role: Mapped[Role] = mapped_column(Role, nullable=False)

project_members_table = Table(
    "project_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("role", SQLEnum(Role), default=Role.DEVELOPER, nullable=False)
)
