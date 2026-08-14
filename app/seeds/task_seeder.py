import random
from faker import Faker
from sqlalchemy import insert

from app.models.user import User
from app.models.project import Project
from app.core.database import db_manager
from app.models.task import Task, TaskStatus
from app.core.security import get_password_hash
from app.models.project_member import ProjectMember, Role

fake = Faker("ru_RU")
Faker.seed(101)
random.seed(101)

# Фиксированные аккаунты для отладки в Swagger
STATIC_USERS = [
    {"email": "owner@pytask.com", "full_name": "Иванов Иван (Владелец)", "role": Role.OWNER},
    {"email": "manager@pytask.com", "full_name": "Петров Петр (Менеджер)", "role": Role.MANAGER},
    {"email": "developer@pytask.com", "full_name": "Сидоров Сидор (Разработчик)", "role": Role.DEVELOPER},
]

JIRA_PROJECTS = [
    {"title": "E-Commerce Платформа (Core API)", "desc": "Разработка высоконагруженного бэкенда интернет-магазина на FastAPI и PostgreSQL."},
    {"title": "Мобильное приложение (iOS/Android)", "desc": "Клиентская часть для покупателей. Интеграция с Core API по REST и WebSockets."},
    {"title": "Платформа данных & Аналитика", "desc": "Сбор метрик, построение ETL процессов и интеграция с ClickHouse хранилищем."}
]

TASK_TEMPLATES = [
    ("Оптимизировать SQL-запросы в репозитории", "Необходимо переписать метод получения дерева через рекурсивный CTE и добавить индексы.", TaskStatus.IN_PROGRESS),
    ("Настроить буферизацию логов ClickHouse", "Внедрить асинхронный flush по таймеру и лимиту батча для разгрузки HTTP пула.", TaskStatus.REVIEW),
    ("Интегрировать JWT аутентификацию", "Добавить генерацию access/refresh токенов, настроить middleware и cookies.", TaskStatus.DONE),
    ("Покрыть тестами эндпоинты комментариев", "Написать pytest-asyncio сценарии для проверки RBAC и каскадного удаления.", TaskStatus.TODO),
    ("Исправить уязвимость IDOR в обновлении задач", "Перевести PATCH методы на get_by_id_secure для валидации прав проекта.", TaskStatus.IN_PROGRESS),
    ("Развернуть инфраструктуру в Docker Compose", "Собрать конфигурацию для api, postgres, redis, clickhouse и mailhog.", TaskStatus.TODO)
]

SUBTASK_TEMPLATES = [
    ("Провести профилирование через EXPLAIN ANALYZE", "Замерить скорость выполнения до и после наката индексов."),
    ("Исправить баг с MissingGreenlet", "Проверить ленивую загрузку связей relationship и добавить selectinload."),
    ("Написать валидационные Pydantic схемы", "Добавить StringConstraints, настроить strip_whitespace и лимиты символов."),
    ("Проверить каскадное удаление (ondelete='CASCADE')", "Убедиться, что при удалении родителя база чистит дочерние таблицы.")
]

async def run_bulk_seed(users_count: int, tasks_count: int):
    session_factory = await db_manager.connect()
    
    if users_count < len(STATIC_USERS):
        users_count = len(STATIC_USERS)
        
    try:
        async with session_factory() as session:
            async with session.begin():
                # --- 1. ГЕНЕРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ ---
                print("👤 Формируем команду инженеров...")
                user_dicts = []
                
                # Добавляем 3 фиксированных аккаунта
                PREHASHED_PASSWORD = get_password_hash("123")
                for static_user in STATIC_USERS:
                    user_dicts.append({
                        "email": static_user["email"],
                        "hashed_password": PREHASHED_PASSWORD,
                        "full_name": static_user["full_name"]
                    })
                    
                # Доращиваем базу случайными сотрудниками до лимита
                for i in range(users_count - len(STATIC_USERS)):
                    user_dicts.append({
                        "email": f"worker_{i}@pytask.com",
                        "hashed_password": PREHASHED_PASSWORD,
                        "full_name": fake.name()
                    })
                    
                user_result = await session.execute(insert(User).returning(User.id), user_dicts)
                user_ids = [row[0] for row in user_result.fetchall()]

                # --- 2. ГЕНЕРАЦИЯ ПРОЕКТОВ ---
                print("📁 Разворачиваем технологические проекты...")
                project_dicts = [
                    {"title": proj["title"], "description": proj["desc"]}
                    for proj in JIRA_PROJECTS
                ]
                project_result = await session.execute(insert(Project).returning(Project.id), project_dicts)
                project_ids = [row[0] for row in project_result.fetchall()]

                # --- 3. МАТЕМАТИЧЕСКОЕ РАСПРЕДЕЛЕНИЕ РОЛЕЙ ---
                print("👥 Формируем проектные группы (RBAC)...")
                member_dicts = []
                
                # Первый проект (Core API) делаем полигоном для тестирования фиксированных ролей
                main_project_id = project_ids[0]
                member_dicts.append({"user_id": user_ids[0], "project_id": main_project_id, "role": Role.OWNER})      # owner@pytask.com
                member_dicts.append({"user_id": user_ids[1], "project_id": main_project_id, "role": Role.MANAGER})    # manager@pytask.com
                member_dicts.append({"user_id": user_ids[2], "project_id": main_project_id, "role": Role.DEVELOPER})  # developer@pytask.com
                
                # Для остальных проектов распределяем роли по классической схеме
                for p_id in project_ids[1:]:
                    # Назначаем случайного владельца (OWNER)
                    member_dicts.append({"user_id": random.choice(user_ids), "project_id": p_id, "role": Role.OWNER})
                    
                # Добавляем случайный рабочий состав на все проекты
                for p_id in project_ids:
                    existing_members = {m["user_id"] for m in member_dicts if m["project_id"] == p_id}
                    # Выбираем случайных инженеров из пула, которых еще нет в проекте
                    available_ids = [uid for uid in user_ids if uid not in existing_members]
                    chosen_devs = random.sample(available_ids, min(4, len(available_ids)))
                    for u_id in chosen_devs:
                        member_dicts.append({"user_id": u_id, "project_id": p_id, "role": Role.DEVELOPER})
                
                await session.execute(insert(ProjectMember), member_dicts)

                # --- 4. МАССОВАЯ ГЕНЕРАЦИЯ КОРНЕВЫХ ЗАДАЧ ---
                print("📌 Наполняем бэклог проекционной массой...")
                task_dicts = []
                for p_id in project_ids:
                    # Ищем список всех участников конкретного проекта для назначения задач
                    allowed_performers = [m["user_id"] for m in member_dicts if m["project_id"] == p_id]
                    
                    for t_idx in range(tasks_count):
                        template = TASK_TEMPLATES[t_idx % len(TASK_TEMPLATES)]
                        task_dicts.append({
                            "title": f"[{t_idx + 1}] {template[0]}",
                            "description": template[1],
                            "status": template[2],
                            "project_id": p_id,
                            "performer_id": random.choice(allowed_performers)
                        })
                
                task_result = await session.execute(insert(Task).returning(Task.id, Task.project_id), task_dicts)
                root_tasks = [(row[0], row[1]) for row in task_result.fetchall()]

                # --- 5. СТРОИТЕЛЬСТВО РЕКУРСИВНОГО ДЕРЕВА ПОДЗАДАЧ ---
                print("🌿 Выстраиваем многоуровневое дерево подзадач (Self-referential)...")
                subtask_dicts = []
                for root_id, p_id in root_tasks:
                    allowed_performers = [m["user_id"] for m in member_dicts if m["project_id"] == p_id]
                    for sub_idx in range(2):
                        sub_template = SUBTASK_TEMPLATES[(root_id + sub_idx) % len(SUBTASK_TEMPLATES)]
                        subtask_dicts.append({
                            "title": f"Подзадача: {sub_template[0]}",
                            "description": sub_template[1],
                            "status": TaskStatus.IN_PROGRESS,
                            "project_id": p_id,
                            "parent_task_id": root_id,
                            "performer_id": random.choice(allowed_performers)
                        })
                
                await session.execute(insert(Task), subtask_dicts)
            
            await session.commit()
            print("✅ Продакшен-сиды успешно зафиксированы в СУБД!")
    finally:
        await db_manager.disconnect()
    