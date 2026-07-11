from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus
from app.schemas.tag import TagResponse

class TaskCreate(BaseModel):
    title: str = Field(..., description="Название задачи")
    description: str | None = Field(None, description="Описание задачи")
    performer_id: int | None = Field(None, description="ID исполнителя задачи")
    parent_task_id: int | None = Field(None, description="ID родительской задачи (если это подзадача)")

class TaskCreateResponse(BaseModel):
    id: int = Field(..., description="ID задачи")
    title: str
    description: str | None
    status: TaskStatus
    project_id: int
    performer_id: int | None
    parent_task_id: int | None
    
    model_config = ConfigDict(from_attributes=True)

class TaskResponse(BaseModel):
    id: int = Field(..., description="ID задачи")
    title: str
    description: str | None
    status: TaskStatus
    project_id: int
    performer_id: int | None
    parent_task_id: int | None

    tags: list[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)
    
class TaskUpdate(BaseModel):
    title: str | None = Field(None, description="Новое название задачи")
    description: str | None = Field(None, description="Новое пописание задачи")
    status: TaskStatus | None = Field(None, description="Новый статус задачи")
    performer_id: int | None = Field(None, description="ID нового исполнителя")
    
    model_config = ConfigDict(from_attributes=True)
    
class TaskTreeResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    project_id: int
    performer_id: int | None
    parent_task_id: int | None
    tags: list[TagResponse] = []
    subtasks: list["TaskTreeResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)
    
TaskTreeResponse.model_rebuild()
