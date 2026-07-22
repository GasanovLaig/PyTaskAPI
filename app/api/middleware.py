import time
from fastapi import Request, Response
import structlog

logger = structlog.get_logger("api.requests")

async def structlog_middleware(request: Request, call_next) -> Response:
    """Асинхронный перехватчик запросов для логирования технических HTTP-сессий."""
    
    start_time = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", "internal-dev-id")
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        ip=request.client.host if request.client else "unknown"
    )
    
    try:
        response: Response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        logger.info(
            "http_request_processed",
            status_code=response.status_code,
            duration_ms=round(process_time, 2)
        )
        
        return response
    except Exception as error:
        process_time = (time.perf_counter() - start_time) * 1000
        logger.error(
            "http_request_failed",
            exception=str(error),
            duration_ms=round(process_time, 2)
        )
        raise error
