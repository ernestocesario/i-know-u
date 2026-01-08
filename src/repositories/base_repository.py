from typing import TypeVar, Generic, List, Optional, Type, Any
from abc import ABC, abstractmethod
from sqlmodel import SQLModel, Session, select

from src.models.DTOs.filters.sql_db.base_filter import BaseFilter

T = TypeVar("T", bound=SQLModel)
F = TypeVar("F", bound=BaseFilter)

class BaseRepository(Generic[T, F], ABC):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model



    # *******************************************************
    # Public methods
    # *******************************************************

    def get_by_id(self, id: str) -> Optional[T]:
        return self.session.get(self.model, id)


    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity


    def update(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity


    def delete(self, entity: T):
        self.session.delete(entity)
        self.session.commit()


    def find(self, filters: F) -> List[T]:
        statement = select(self.model)

        # Apply custom filters
        statement = self._apply_custom_filters(statement, filters)

        # Apply sorting
        statement = self._apply_sorting(statement, filters)

        # Apply pagination
        statement = self._apply_pagination(statement, filters)

        results = self.session.exec(statement).all()

        return list(results)



    # *******************************************************
    # Private methods
    # *******************************************************

    @abstractmethod
    def _apply_custom_filters(self, statement: Any, filters: F) -> Any:
        """
        Children classes should override this method to implement specific filtering logic.
        Apply filters to the given SQLAlchemy statement.
        :param statement:
        :param filters:
        :return:
        """
        return statement


    def _apply_sorting(self, statement: Any, filters: BaseFilter) -> Any:
        if not filters.sort_by:
            return statement

        sort_column = getattr(self.model, filters.sort_by, None)

        if sort_column is None:
            return statement

        if filters.sort_order == "desc":
            statement = statement.order_by(sort_column.desc())
        else:
            statement = statement.order_by(sort_column.asc())

        return statement


    def _apply_pagination(self, statement: Any, filters: BaseFilter) -> Any:
        if filters.offset is not None:
            statement = statement.offset(filters.offset)

        if filters.limit is not None:
            statement = statement.limit(filters.limit)

        return statement