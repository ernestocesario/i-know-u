from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime

from sqlmodel import select

from .base_repository import BaseRepository
from ..models import Story
from ..models.DTOs.filters.story_filter import StoryFilter


if TYPE_CHECKING:
    from ..models import Person


class StoryRepository(BaseRepository[Story, StoryFilter]):
    def __init__(self, session):
        super().__init__(session, Story)


    # *******************************************************
    # Public methods
    # *******************************************************

    def get_by_external_id(self, external_id: str) -> Optional[Story]:
        statement = (
            select(Story)
            .where(Story.external_id == external_id)
        )

        return self.session.exec(statement).first()



    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: StoryFilter) -> Any:
        if filters.min_publication_datetime:
            statement = self._apply_min_publication_datetime(statement, filters.min_publication_datetime)

        if filters.max_publication_datetime:
            statement = self._apply_max_publication_datetime(statement, filters.max_publication_datetime)

        if filters.processed is not None:
            statement = self._apply_processed(statement, filters.processed)

        if filters.owner_is:
            statement = self._apply_owner_is(statement, filters.owner_is)

        return statement


    @staticmethod
    def _apply_min_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Story.publication_datetime >= value)

    @staticmethod
    def _apply_max_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Story.publication_datetime <= value)

    @staticmethod
    def _apply_processed(statement: Any, value: bool) -> Any:
        return statement.where(Story.processed == value)

    @staticmethod
    def _apply_owner_is(statement: Any, value: Person) -> Any:
        return statement.where(Story.owner_id == value.id)