from pydantic import BaseModel, ConfigDict, Field

class CommentCreate(BaseModel):
    text: str = Field(..., description="Текст комметария")
    parent_comment_id: int | None = Field(None, description="ID родительского комментария")

class CommentResponse(BaseModel):
    id: int = Field(..., description="ID комментария")
    text: str
    task_id: int
    author_id: int
    parent_comment_id: int | None

    model_config = ConfigDict(from_attributes=True)
