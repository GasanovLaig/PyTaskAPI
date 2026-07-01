from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.uow import get_uow
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.services.uow import UnitOfWork

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    uow: UnitOfWork = Depends(get_uow)
) -> User:
    auth_service = AuthService(uow)
    
    return await auth_service.register_new_user(user_data)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: UnitOfWork = Depends(get_uow)
) -> dict:
    auth_service = AuthService(uow)
    
    token = await auth_service.authenticate_user(
        email=form_data.username,
        plain_password=form_data.password
    )
    
    return {"access_token": token, "token_type": "bearer"}
