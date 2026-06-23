from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    title: str = Field(..., description="Название проекта")
    description: str | None = Field(description="Описание проекта")

class ProjectResponse(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор проекта")
    title: str
    description: str | None

    class Config:
        from_attributes = True
