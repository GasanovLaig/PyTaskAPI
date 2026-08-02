class AppError(Exception):
    """Базовое исключение для всего приложения."""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)
        
class ResourceNotFoundError(AppError):
    """Исключение, если объект не найден (замена для 404)."""
    pass

class ResourceAlreadyExistsError(AppError):
    """Исключение, если объект нарушает уникальность (замена для HTTP 409)."""
    pass

class DatabaseDeadlockError(AppError):
    """Исключение при возникновении взаимной блокировки в СУБД (HTTP 409 или 503)."""
    pass

class InvalidCredentialsError(AppError):
    """Исключение, если пользователь ввел неверный email или пароль (HTTP 401)."""
    pass

class AccessDeniedError(AppError):
    """Исключение для ошибок прав доступа (замена для HTTP 403)."""
    pass

class QueueServiceUnavailableError(AppError):
    """Исключение, если сервис очередей задач (ARQ/Redis) недоступен (HTTP 503)."""
    pass
