from typing import Any, Generic, Type, TypeVar
from sqlalchemy import Sequence, delete, select, update
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
        options: Sequence[ExecutableOption] | None = None,
        populate_existing: bool = False
    ) -> ModelType | None:
        return await self.session.get(
            self.model,
            obj_id,
            options=options,
            populate_existing=populate_existing
        )
    
    async def get_all(self) -> list[ModelType]:
        result = await self.session.scalars(select(self.model))
        
        return result.all()
    
    async def create(self, data: dict[str, Any]) -> ModelType:
        new_obj = self.model(**data)
        self.session.add(new_obj)
        
        return new_obj
        
    async def update(self, obj: Type[ModelType], data: dict[str, Any]) -> ModelType | None:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
                
        self.session.add(obj)
        
        return obj
    
    async def update_by_id(self, obj_id: int, data: dict[str, Any]) -> ModelType | None:
        query = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        
        return result.scalar_one_or_none()
    
    async def delete(self, obj: Type[ModelType]):
        await self.session.delete(obj)
        
    async def delete_by_id(self, obj_id: int):
        await self.session.execute(
            delete(self.model)
            .where(self.model.id == obj_id)
        )
        