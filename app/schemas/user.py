from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, StringConstraints

UserFullNameStr = Annotated[str, StringConstraints(min_length=2, max_length=100, strip_whitespace=True)]

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    full_name: UserFullNameStr = Field(..., description="Полное имя пользователя")
    
class UserCreate(UserBase):
    password: SecretStr = Field(..., exclude=True, min_length=3, description="Сырой пароль пользователя")
    
class UserResponse(UserBase):
    id: int = Field(..., gt=0, description="ID пользователя")
    
    model_config = ConfigDict(from_attributes=True)
    