from typing import Any
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Identity, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(50), index=True)
    resource_type: Mapped[str] = mapped_column(String(50))
    resource_id: Mapped[int | None] = mapped_column(index=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
