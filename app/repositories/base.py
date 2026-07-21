from typing import Any, Generic, Type, TypeVar
from sqlalchemy import delete, exists, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        
    async def create(self, data: dict[str, Any]) -> ModelType:
        new_obj = await self.session.scalar(
            insert(self.model)
            .values(**data)
            .returning(self.model)
        )
        
        return new_obj
                    
    async def is_exists_in_project(self, obj_id: int, project_id: int) -> bool:
        query = select(exists().where(
            self.model.id == obj_id,
            self.model.project_id == project_id
        ))
        result = await self.session.execute(query)
        
        return bool(result)
    
    async def get_all(self) -> list[ModelType]:
        result = await self.session.scalars(select(self.model))
        
        return result.all()
        
    async def update_by_id(self, obj_id: int, data: dict[str, Any]) -> ModelType | None:
        return await self.session.scalar(
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data)
            .returning(self.model)
        )
        
    async def update_by_id_secure(self, obj_id: int, project_id: int, data: dict[str, Any]) -> ModelType | None:
        return await self.session.scalar(
            update(self.model)
            .where(
                self.model.id == obj_id,
                self.model.project_id == project_id
            )
            .values(**data)
            .returning(self.model)
        )
    
    async def delete_by_id(self, obj_id: int) -> bool:
        result = await self.session.execute(
            delete(self.model)
            .where(self.model.id == obj_id)
        )
        
        return result.rowcount > 0
        
    async def delete_by_id_secure(self, obj_id: int, project_id: int) -> bool:
        result = await self.session.execute(
            delete(self.model)
            .where(
                self.model.id == obj_id,
                self.model.project_id == project_id
            )
        )
        
        return result.rowcount > 0
        