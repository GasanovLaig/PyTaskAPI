from fastapi import HTTPException, status

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    async def register_new_user(self, user_data: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже зарегистрирован"
            )
        
        hashed_pwd = get_password_hash(user_data.password)
        db_data = {
            "email": user_data.email,
            "hashed_password": hashed_pwd,
            "full_name": user_data.full_name
        }
        
        return await self.user_repo.create(db_data)
    
    async def authenticate_user(self, email: str, plain_password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        if not verify_password(plain_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        token_data = {"sub": user.email}
        access_token = create_access_token(token_data)
        
        return access_token
    