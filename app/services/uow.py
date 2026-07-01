from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment import CommentRepository
from app.repositories.project import ProjectRepository
from app.repositories.tag import TagRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository

class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def __aenter__(self):
        self.users = UserRepository(self.session)
        self.projects = ProjectRepository(self.session)
        self.tasks = TaskRepository(self.session)
        self.tags = TagRepository(self.session)
        self.comments = CommentRepository(self.session)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
            
        await self.session.close()
        
    async def commit(self):
        await self.session.commit()
        
    async def refresh(self, obj):
        await self.session.refresh(obj)
        
    async def rollback(self):
        await self.session.rollback()
