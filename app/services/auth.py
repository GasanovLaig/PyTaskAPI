from app.core.exceptions import InvalidCredentialsError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.uow import UnitOfWork

class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    async def register_new_user(self, user_data: UserCreate) -> User:
        async with self.uow:
            hashed_password = get_password_hash(user_data.password.get_secret_value())
            db_data = user_data.model_dump(exclude="password")
            db_data["hashed_password"] = hashed_password
            
            new_user = await self.uow.users.create(db_data)
            await self.uow.commit()
            
            return new_user
            
    async def authenticate_user(self, email: str, plain_password: str) -> str:
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if not user or not verify_password(plain_password, user.hashed_password):
                raise InvalidCredentialsError("Неверный email или пароль")
            
            token_data = {"sub": user.email}
            access_token = create_access_token(token_data)
            
            return access_token
    