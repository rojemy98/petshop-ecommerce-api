from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def get_all(self) -> list[ModelType]:
        statement = select(self.model)

        result = self.session.execute(statement)

        return list(result.scalars().all())

    def create(self, entity: ModelType) -> ModelType:
        try:
            self.session.add(entity)
            self.session.flush()

            return entity

        except SQLAlchemyError:
            self.session.rollback()
            raise

    def update(self, entity: ModelType) -> ModelType:
        try:
            self.session.flush()

            return entity

        except SQLAlchemyError:
            self.session.rollback()
            raise

    def delete(self, entity: ModelType) -> None:
        try:
            self.session.delete(entity)
            self.session.flush()

        except SQLAlchemyError:
            self.session.rollback()
            raise