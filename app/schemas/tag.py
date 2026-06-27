from pydantic import BaseModel, ConfigDict, Field

class TagCreate(BaseModel):
    name: str = Field(..., description="Название тега")

class TagResponse(BaseModel):
    id: int = Field(..., description="ID тега")
    name: str
        
    model_config = ConfigDict(from_attributes=True)
