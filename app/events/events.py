from dataclasses import dataclass

@dataclass(frozen=True)
class TaskCreatedEvent:
    """Событие: Новая задача успешно создана в базе данных."""
    task_id: int
    project_id: int
    task_title: str
    task_status: str
    performer_id: int | None
    current_user_id: int
    notify_metadata: dict

@dataclass(frozen=True)
class TaskUpdatedEvent:
    """Событие: Задача успешно обновлена."""
    task_id: int
    project_id: int
    current_user_id: int
    db_data: dict
    old_metadata: dict
    new_metadata: dict
    notify_metadata: dict

@dataclass(frozen=True)
class TaskDeletedEvent:
    """Событие: Задача безвозвратно удалена."""
    task_id: int
    project_id: int
    current_user_id: int

@dataclass(frozen=True)
class UserRegisteredEvent:
    """Событие: Новый сотрудник зарегистрирован."""
    user_id: int
    email: str

@dataclass(frozen=True)
class AuthFailedEvent:
    """Событие: Неудачная попытка входа."""
    attempted_email: str

@dataclass(frozen=True)
class AuthLoginEvent:
    """Событие: Успешный вход в систему."""
    user_id: int

@dataclass(frozen=True)
class ProjectCreatedEvent:
    """Событие: Создан новый проект."""
    project_id: int
    project_title: str
    current_user_id: int

@dataclass(frozen=True)
class ProjectMemberAddedEvent:
    """Событие: В проект добавлен новый участник."""
    project_id: int
    user_id: int
    role: str
    current_user_id: int

@dataclass(frozen=True)
class ProjectUpdatedEvent:
    """Событие: Изменены настройки проекта."""
    project_id: int
    current_user_id: int
    updated_fields: list[str]

@dataclass(frozen=True)
class ProjectDeletedEvent:
    """Событие: Проект удален."""
    project_id: int
    current_user_id: int

@dataclass(frozen=True)
class TagCacheInvalidationEvent:
    """Событие: Структура тегов изменена (требуется сброс кэша дерева задач)."""
    project_id: int
