from arq import ArqRedis
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.arq import get_arq_pool
from app.models.user import User
from app.services.uow import UnitOfWork
from app.services.auth import AuthService
from app.api.dependencies.uow import get_uow
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Аутентификация"])

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    uow: UnitOfWork = Depends(get_uow),
    arq_pool: ArqRedis = Depends(get_arq_pool)
) -> User:
    auth_service = AuthService(uow, arq_pool)
    
    return await auth_service.register_new_user(user_data)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: UnitOfWork = Depends(get_uow),
    arq_pool: ArqRedis = Depends(get_arq_pool)
) -> dict:
    auth_service = AuthService(uow, arq_pool)
    
    token = await auth_service.authenticate_user(
        email=form_data.username,
        plain_password=form_data.password
    )
    
    return {"access_token": token, "token_type": "bearer"}
