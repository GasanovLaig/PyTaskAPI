from pydantic import BaseModel, ConfigDict, Field

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, strip_whitespace=True, description="Текст комметария")
    parent_comment_id: int | None = Field(None, gt=0, description="ID родительского комментария")
    
class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: str = Field(..., min_length=1, strip_whitespace=True, description="Обновленный текст комметария")
    
class CommentResponse(CommentBase):
    id: int = Field(..., gt=0, description="ID комментария")
    task_id: int = Field(..., gt=0, description="ID задачи")
    author_id: int = Field(..., gt=0, description="ID автора")
    
    model_config = ConfigDict(from_attributes=True)
