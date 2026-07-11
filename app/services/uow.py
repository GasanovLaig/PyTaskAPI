from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.tag import TagRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository

class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        
        self._users = None
        self._projects = None
        self._tasks = None
        self._tags = None
        self._comments = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
    
    @property
    def users(self) -> UserRepository:
        if self._users is None:
            self._users = UserRepository(self.session)
            
        return self._users
    
    @property
    def projects(self) -> ProjectRepository:
        if self._projects is None:
            self._projects = ProjectRepository(self.session)
            
        return self._projects
    
    @property
    def tasks(self) -> TaskRepository:
        if self._tasks is None:
            self._tasks = TaskRepository(self.session)
            
        return self._tasks
    
    @property
    def tags(self) -> TagRepository:
        if self._tags is None:
            self._tags = TagRepository(self.session)
            
        return self._tags

    @property
    def comments(self) -> CommentRepository:
        if self._comments is None:
            self._comments = CommentRepository(self.session)
            
        return self._comments
        
    async def commit(self):
        await self.session.commit()
        
    async def rollback(self):
        await self.session.rollback()
