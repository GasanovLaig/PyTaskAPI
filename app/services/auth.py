from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.uow import UnitOfWork

class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def register_new_user(self, user_data: UserCreate) -> User:
        async with self.uow:
            hashed_pwd = get_password_hash(user_data.password)
            db_data = {
                "email": user_data.email,
                "hashed_password": hashed_pwd,
                "full_name": user_data.full_name
            }
            
            try:
                new_user = await self.uow.users.create(db_data)
                await self.uow.commit()
                
                return new_user
            
            except IntegrityError:
                await self.uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с таким email уже зарегистрирован"
                )
    
    async def authenticate_user(self, email: str, plain_password: str) -> str:
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
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
    