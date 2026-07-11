from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus
from app.schemas.tag import TagResponse

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, strip_whitespace=True, description="Название задачи")
    description: str | None = Field(None, description="Описание задачи")
    performer_id: int | None = Field(None, gt=0, description="ID исполнителя задачи")
    parent_task_id: int | None = Field(None, gt=0, description="ID родительской задачи")
    
class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100, strip_whitespace=True, description="Новое название задачи")
    description: str | None = Field(None, description="Новое описание задачи")
    status: TaskStatus | None = Field(None, description="Новый статус задачи")
    performer_id: int | None = Field(None, gt=0, description="ID нового исполнителя")

    model_config = ConfigDict(from_attributes=True)
    
class TaskCreateUpdateResponse(TaskBase):
    id: int = Field(..., gt=0, description="ID задачи")
    status: TaskStatus = Field(..., description="Текущий статус задачи")
    project_id: int = Field(..., gt=0, description="ID проекта")

    model_config = ConfigDict(from_attributes=True)
    
class TaskResponse(TaskCreateUpdateResponse):
    tags: list[TagResponse] = Field([], description="Список прикрепленных тегов")
    
class TaskTreeResponse(TaskResponse):
    subtasks: list["TaskTreeResponse"] = Field([], description="Список дочерних задач")
    
TaskTreeResponse.model_rebuild()
