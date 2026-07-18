from typing import Annotated
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
    