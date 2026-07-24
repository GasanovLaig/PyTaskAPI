from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from main import app
from app.core.database import Base, get_db
from tests.factories import ProjectFactory, UserFactory, TaskFactory

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:NOPASSWOR@localhost:5432/pytaskapi_test"

@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Создает фабрику подключений один раз на всю сессию тестов."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    yield engine
    
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
        base_url="http://test"
    ) as async_client:
        yield async_client
        
    app.dependency_overrides.clear()
    