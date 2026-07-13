from typing import Any, Generic, Type, TypeVar
from sqlalchemy import Sequence, delete, exists, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

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
        
    async def get_by_id_secure(self, obj_id: int, project_id: int) -> ModelType | None:
        if hasattr(self.model, "project_id"):
            return await self.session.scalar(
                select(self.model)
                .where(
                    self.model.id == obj_id,
                    self.model.project_id == project_id
                )
            )
            
        return await self.get_by_id(obj_id)
        
    async def is_exists_in_project(self, obj_id: int, project_id: int) -> bool:
        query = select(exists().where(
            self.model.id == obj_id,
            self.model.project_id == project_id
        ))
        result = await self.session.execute(query)
        
        return bool(result)
    
    async def is_exists(self, obj_id: int) -> bool:
        return bool(await self.session.execute(
            select(exists().where(self.model.id == obj_id))
            ))
    
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
                self.project_id == project_id
            )
            .values(**data)
            .returning(self.model)
        )
    
    async def delete_by_id(self, obj_id: int):
        return await self.session.scalar(
            delete(self.model)
            .where(self.model.id == obj_id)
            .returning(self.model.id)
        )
        
    async def delete_by_id_secure(self, obj_id: int, project_id: int):
        if hasattr(self.model, "project_id"):
            result = await self.session.scalar(
                delete(self.model)
                .where(
                    self.model.id == obj_id,
                    self.model.project_id == project_id
                )
                .returning(self.model.id)
            )
            
            return result
        
        return await self.delete_by_id(obj_id)
        