from pydantic import BaseModel, Field

class TagCreate(BaseModel):
    name: str = Field(..., description="Название тега")

class TagResponse(BaseModel):
    id: int = Field(..., description="ID тега")
    name: str

    class Config:
        from_attributes = True
