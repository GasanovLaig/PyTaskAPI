from pydantic import BaseModel, ConfigDict, Field

class ProjectBase(BaseModel):
    description: str | None = Field(None, description="Описание проекта")
    
class ProjectCreate(ProjectBase):
    title: str = Field(..., min_length=1, max_length=100, strip_whitespace=True, description="Название проекта")
    
class ProjectUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100, strip_whitespace=True, description="Новое название проекта")
    description: str | None = Field(None, description="Новое описание проекта")
    
class ProjectResponse(ProjectCreate):
    id: int = Field(..., gt=0, description="ID проекта")
    
    model_config = ConfigDict(from_attributes=True)
    