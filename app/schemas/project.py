from pydantic import BaseModel, ConfigDict, Field

class ProjectCreate(BaseModel):
    title: str = Field(..., description="Название проекта")
    description: str | None = Field(description="Описание проекта")

class ProjectResponse(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор проекта")
    title: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
    
class ProjectUpdate(BaseModel):
    title: str = Field(None, description="Новое название проекта")
    description: str = Field(None, description="Новое описание проекта")
    
    model_config = ConfigDict(from_attributes=True)
