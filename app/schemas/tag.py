from pydantic import BaseModel, ConfigDict, Field

class TagCreate(BaseModel):
    name: str = Field(..., description="Название тега")

class TagResponse(BaseModel):
    id: int = Field(..., description="ID тега")
    name: str
    project_id: int = Field(..., description="ID проекта, к которому привязан тег")
        
    model_config = ConfigDict(from_attributes=True)
