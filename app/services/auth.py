
from fastapi import HTTPException

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def register_new_user(self, user_data: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=404, detail="Пользователь с таким email уже зарегистрирован")
        
        db_data = {
            "email": user_data.email,
            "password": user_data.password,
            "full_name": user_data.full_name
        }
        
        return await self.user_repo.create(db_data)
    