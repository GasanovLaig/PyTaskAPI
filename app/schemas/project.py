from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.project_member import Role

ProjectTitleStr = Annotated[str, StringConstraints(min_length=1, max_length=100, strip_whitespace=True)]

class ProjectBase(BaseModel):
    description: str | None = Field(None, description="Описание проекта")
    
class ProjectCreate(ProjectBase):
    title: ProjectTitleStr = Field(..., description="Название проекта")
    
class ProjectUpdate(BaseModel):
    title: ProjectTitleStr | None = Field(None, description="Новое название проекта")
    description: str | None = Field(None, description="Новое описание проекта")
    
class ProjectResponse(ProjectCreate):
    id: int = Field(..., gt=0, description="ID проекта")
    
    model_config = ConfigDict(from_attributes=True)
    
class ProjectMemberAdd(BaseModel):
    user_id: int = Field(..., gt=0, description="ID добавляемого сотрудника")
    role: Role = Field(Role.DEVELOPER, description="Роль сотрудника в проекте")
    
class ReportTaskResponse(BaseModel):
    task_id: str = Field(..., description="ID фоновой задачи Celery")
    status: str = Field("Pending", description="Текущий статус обработки задачи")
    
class ReportStatusResponse(BaseModel):
    task_id: str = Field(..., description="ID задачи")
    status: str = Field(..., description="Статус выполнения (PENDING, STARTED, SUCCESS, FAILURE)")
    result: Any | None = Field(..., description="Результат выполнения задачи (сгенерированный отчет), если она готова")
    