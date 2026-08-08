import asyncio
import structlog
from typing import Type, Callable, List, Dict, Any, Awaitable

logger = structlog.get_logger("infra.events")

HandlerType = Callable[[Any], Awaitable[None]]

class EventBus:
    def __init__(self):
        self._listeners: Dict[Type[Any], List[HandlerType]] = {}
        
    def _get_handler_name(self, handler: HandlerType) -> str:
        """Безопасно извлекает имя хендлера, даже если это метод класса."""
        return getattr(handler, "__name__", type(handler).__name__)
        
    def register(self, event_type: Type[Any], handler: HandlerType):
        """Регистрирует хендлер для определенного типа события."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
            
        self._listeners[event_type].append(handler)
        logger.debug(
            "Registered event handler",
            event_type=event_type.__name__,
            handler=handler.__name__
        )
        
    async def publish(self, event_name: Any):
        """Публикует событие и асинхронно запускает все связанные хендлеры."""
        event_type = type(event_name)
        handlers = self._listeners.get(event_type, [])
        
        if not handlers:
            logger.warning("No handlers registered for event", event_type=event_type.__name__)
            return
        
        for handler in handlers:
            asyncio.create_task(self._run_handler(handler, event_name))
            
    async def _run_handler(self, handler: HandlerType, event_name: Any):
        handler_name = self._get_handler_name(handler)
        try:
            await handler(event_name)
        except Exception as error:
            logger.error(
                "Event handler failed",
                event_type=type(event_name).__name__,
                handler=handler_name,
                error=str(error)
            )
            
event_bus = EventBus()
