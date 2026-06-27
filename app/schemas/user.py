from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., description="Сырой пароль пользователя")
    full_name: str = Field(..., description="Полное имя пользователя")

class UserResponse(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)
