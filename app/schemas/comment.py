from pydantic import BaseModel, Field

class CommentCreate(BaseModel):
    text: str = Field(..., description="Текст комметария")
    author_id: int = Field(..., description="Автор комментария")
    parent_comment_id: int | None = Field(None, description="ID родительского комментария")

class CommentResponse(BaseModel):
    id: int = Field(..., description="ID комментария")
    text: str
    task_id: int
    author_id: int
    parent_comment_id: int | None

    class Config:
        from_attributes = True
