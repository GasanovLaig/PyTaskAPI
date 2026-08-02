from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    QueueServiceUnavailableError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    DatabaseDeadlockError,
    InvalidCredentialsError,
    AccessDeniedError
)

async def global_unhandled_exception_handler(request:Request, exception: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера. Мы уже работаем над ее исправлением."}
    )
    
async def pydantic_validation_exception_handler(request: Request, exception: RequestValidationError):
    errors = [f"{'.'.join(str(p) for p in error['loc'][1:])}: {error['msg']}" for error in exception.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "; ".join(errors)}
    )

async def resource_already_exists_handler(request: Request, exception: ResourceAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exception.detail}
    )
    
async def resource_not_found_handler(request: Request, exception: ResourceNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exception.detail}
    )
    
async def database_deadlock_handler(request: Request, exception: DatabaseDeadlockError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": exception.detail}
    )
    
async def invalid_credentials_handler(request: Request, exception: InvalidCredentialsError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exception.detail}
    )
    
async def access_denied_handlers(request: Request, exception: AccessDeniedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exception.detail}
    )
    
async def queue_service_unavailable_handler(request: Request, exception: QueueServiceUnavailableError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Сервис создания отчетов временно недоступен. Пожалуйста, повторите попытку позже."}
    )
    
def register_exception_handlers(app: FastAPI) -> None:
    """Централизованная регистрация всех обработчиков исключений приложения."""
    app.add_exception_handler(Exception, global_unhandled_exception_handler)
    app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(ResourceAlreadyExistsError, resource_already_exists_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
    app.add_exception_handler(DatabaseDeadlockError, database_deadlock_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
    app.add_exception_handler(AccessDeniedError, access_denied_handlers)
    app.add_exception_handler(QueueServiceUnavailableError, queue_service_unavailable_handler)
