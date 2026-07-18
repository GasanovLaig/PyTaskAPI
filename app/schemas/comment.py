from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

CommentTextStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]

class CommentBase(BaseModel):
    text: CommentTextStr = Field(..., description="Текст комметария")
    parent_comment_id: int | None = Field(None, gt=0, description="ID родительского комментария")
    
class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: CommentTextStr = Field(..., description="Обновленный текст комметария")
    
class CommentResponse(CommentBase):
    id: int = Field(..., gt=0, description="ID комментария")
    task_id: int = Field(..., gt=0, description="ID задачи")
    author_id: int = Field(..., gt=0, description="ID автора")
    
    model_config = ConfigDict(from_attributes=True)
