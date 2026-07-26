import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.core.security import get_password_hash

PRE_HASHED_PASSWORD = get_password_hash("password123")

class AsyncSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
    
    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session
        obj = model_class(*args, **kwargs)
        session.add(obj)
        await session.flush()
        
        return obj
    
class UserFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = User
        
    email = factory.Sequence(lambda n: f"developer_{n}@pytask.com")
    full_name = factory.Faker("name", locale="ru_RU")
    hashed_password = PRE_HASHED_PASSWORD

class ProjectFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Project
        
    title = factory.Sequence(lambda n: f"Проект Автоматизации №{n}")
    description = factory.Faker("catch_phrase", locale="ru_RU")

class TaskFactory(AsyncSQLAlchemyModelFactory):
    class Meta:
        model = Task
        
    title = factory.Sequence(lambda n: f"Разработать фичу №{n}")
    description = factory.Faker("sentence", locale="ru_RU")
    status = TaskStatus.TODO
    project_id = None
    performer_id = None
    parent_task_id = None
