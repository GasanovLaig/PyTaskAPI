import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from main import app
from app.core.database import Base, get_db
from app.core.config import Settings, settings
from app.worker.celery_app import celery_app
from tests.factories import ProjectFactory, UserFactory, TaskFactory

MAIN_DB_NAME_TO_BAN = settings.DB_NAME.lower()
# Переопределение глобальной переменной REDIS_URL настроек pydantic-settings объекта settings для celery_app
settings_dict = Settings(_env_file=".env.tests", _env_prefix="TEST_").model_dump()
for key, value in settings_dict.items():
    setattr(settings, key, value)
celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL

TEST_DATABASE_URL = settings.DATABASE_URL_ASYNC

@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Создает фабрику подключений один раз на всю сессию тестов."""
    TEST_DB_NAME = settings.DB_NAME.lower()
    if ("test" not in TEST_DB_NAME
        or TEST_DB_NAME in [MAIN_DB_NAME_TO_BAN, "pytaskapi_dev_db", "pytaskapi_db", "pytaskapi", "postgres"]):
        raise RuntimeError(
            f"ОПАСНОСТЬ: Попытка запустить тесты на основной БД '{settings.DB_NAME}'."
        )
        
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest.fixture(scope="session", autouse=True)
async def setup_database(db_engine: AsyncEngine):
    """Создает таблицы один раз перед стартом тестов и удаляет в конце."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    yield

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
@pytest.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Создает изолированную сессию для каждого теста.
    Использует режим 'create_savepoint', чтобы перехватывать внутренние коммиты FastAPI.
    """
    async with db_engine.connect() as connection:
        async with connection.begin() as _:
            async_session_factory = async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                autoflush=False,
                join_transaction_mode="create_savepoint"
            )
            async with async_session_factory() as session:
                UserFactory._meta.sqlalchemy_session = session
                ProjectFactory._meta.sqlalchemy_session = session
                TaskFactory._meta.sqlalchemy_session = session
                
                yield session
                UserFactory._meta.sqlalchemy_session = None
                ProjectFactory._meta.sqlalchemy_session = None
                TaskFactory._meta.sqlalchemy_session = None
                await session.rollback()
        
@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Клиент FastAPI с автоматическим переопределением зависимости сессии."""
    async def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000"
    ) as async_client:
        yield async_client
        
    app.dependency_overrides.clear()
    