from pydantic import BaseModel, ConfigDict, Field

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True, description="Название тега")
    
class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int = Field(..., gt=0, description="ID тега")
    project_id: int = Field(..., gt=0, description="ID проекта, к которому привязан тег")
    
    model_config = ConfigDict(from_attributes=True)
