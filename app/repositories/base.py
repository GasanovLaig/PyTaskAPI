from typing import Any, Generic, Type, TypeVar
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        
    async def get_by_id(
        self,
        obj_id: int,
        options: Sequence[ExecutableOption] | None = None
    ) -> ModelType | None:
        return await self.session.get(self.model, obj_id, options=options)
    
    async def get_all(self) -> list[ModelType]:
        result = await self.session.scalars(select(self.model))
        
        return result.all()
    
    async def create(self, data: dict[str, Any]) -> ModelType:
        new_obj = self.model(**data)
        self.session.add(new_obj)
        
        await self.session.commit()
        await self.session.refresh(new_obj)
        
        return new_obj
    
    async def delete(self, obj):
        await self.session.delete(obj)
        await self.session.commit()
        
    async def update(self, obj_id: int, data: dict[str, Any]) -> ModelType | None:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
                
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        
        return obj
