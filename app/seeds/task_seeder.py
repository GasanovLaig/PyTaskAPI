import random
from faker import Faker
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember, Role
from app.models.task import Task, TaskStatus
from app.core.security import get_password_hash

# Фиксируем генераторы для детерминированности данных
fake = Faker("ru_RU")
Faker.seed(42)
random.seed(42)

async def run_bulk_seed(users_count: int, tasks_count: int):
    engine = create_async_engine(settings.DATABASE_URL_ASYNC)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    async with session_factory() as session:
        async with session.begin():
            # --- 1. ГЕНЕРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ ---
            print("👤 Генерируем пользователей...")
            user_dicts = [
                {
                    "email": f"worker_{i}@company.com",
                    "hashed_password": get_password_hash("password123"),
                    "full_name": fake.name()
                }
                for i in range(users_count)
            ]
            user_result = await session.execute(insert(User).returning(User.id), user_dicts)
            user_ids = [row[0] for row in user_result.fetchall()]

            # --- 2. ГЕНЕРАЦИЯ ПРОЕКТОВ ---
            print("📁 Генерируем проекты...")
            project_dicts = [
                {
                    "title": f"Проект: {fake.catch_phrase()}",
                    "description": fake.text(max_nb_chars=150)
                }
                for _ in range(3)
            ]
            project_result = await session.execute(insert(Project).returning(Project.id), project_dicts)
            project_ids = [row[0] for row in project_result.fetchall()]

            # --- 3. ГЕНЕРАЦИЯ УЧАСТНИКОВ ПРОЕКТА ---
            print("👥 Распределяем роли участников...")
            member_dicts = []
            for p_id in project_ids:
                # Назначаем первого юзера OWNER-ом
                member_dicts.append({"user_id": user_ids[0], "project_id": p_id, "role": Role.OWNER})
                # Остальных (до 6 человек) делаем разработчиками
                for u_id in user_ids[1:6]:
                    member_dicts.append({"user_id": u_id, "project_id": p_id, "role": Role.DEVELOPER})
            
            await session.execute(insert(ProjectMember), member_dicts)

            # --- 4. МАССОВАЯ ГЕНЕРАЦИЯ КОРНЕВЫХ ЗАДАЧ ---
            print("📌 Создаем корневые задачи...")
            task_dicts = []
            for p_id in project_ids:
                for t_idx in range(tasks_count):
                    task_dicts.append({
                        "title": f"Задача {fake.word().capitalize()}: {fake.sentence(nb_words=3)}",
                        "description": fake.paragraph(nb_sentences=2),
                        "status": random.choice(list(TaskStatus)),
                        "project_id": p_id,
                        "performer_id": random.choice(user_ids)
                    })
            
            task_result = await session.execute(insert(Task).returning(Task.id, Task.project_id), task_dicts)
            # Собираем кортежи (id, project_id) для генерации подзадач
            root_tasks = [(row[0], row[1]) for row in task_result.fetchall()]

            # --- 5. МАССОВАЯ ГЕНЕРАЦИЯ ПОДЗАДАЧ (Дерево задач) ---
            print("🌿 Выстраиваем дерево подзадач (Self-referential)...")
            subtask_dicts = []
            for root_id, p_id in root_tasks:
                for sub_idx in range(2): # По 2 подзадачи на каждую корневую задачу
                    subtask_dicts.append({
                        "title": f"Подзадача к #{root_id} [{sub_idx}]",
                        "description": fake.sentence(),
                        "status": TaskStatus.IN_PROGRESS,
                        "project_id": p_id,
                        "parent_task_id": root_id,
                        "performer_id": random.choice(user_ids)
                    })
            
            await session.execute(insert(Task), subtask_dicts)
        
        await session.commit()
        print("✅ База данных успешно наполнена детерминированными сидами!")
    
    await engine.dispose()
