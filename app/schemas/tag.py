from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

TagNameStr = Annotated[str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)]

class TagBase(BaseModel):
    name: TagNameStr = Field(..., description="Название тега")
    
class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int = Field(..., gt=0, description="ID тега")
    project_id: int = Field(..., gt=0, description="ID проекта, к которому привязан тег")
    
    model_config = ConfigDict(from_attributes=True)
