from pydantic import BaseModel, Field

from app.models.task import TaskStatus
from app.schemas.tag import TagResponse

class TaskCreate(BaseModel):
    title: str = Field(..., description="Название задачи")
    description: str | None = Field(None, description="Описание задачи")
    performer_id: int | None = Field(None, description="ID исполнителя задачи")
    parent_task_id: int | None = Field(None, description="ID родительской задачи (если это подзадача)")

class TaskResponse(BaseModel):
    id: int = Field(..., description="ID задачи")
    title: str
    description: str | None
    status: TaskStatus
    project_id: int
    performer_id: int | None
    parent_task_id: int | None

    tags: list[TagResponse] = []

    class Config:
        from_attributes = True
