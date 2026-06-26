from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    user_repository = UserRepository(session=db)
    auth_service = AuthService(user_repo=user_repository)
    
    return await auth_service.register_new_user(user_data=user_data)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> dict:
    user_repository = UserRepository(session=db)
    auth_service = AuthService(user_repo=user_repository)
    
    token = await auth_service.authenticate_user(
        email=form_data.username,
        plain_password=form_data.password
    )
    
    return {"access_token": token, "token_type": "bearer"}
