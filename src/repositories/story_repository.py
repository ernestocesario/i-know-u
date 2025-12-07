from typing import Optional, Any, TYPE_CHECKING
from datetime import date

from .base_repository import BaseRepository
from ..models import Story
from ..models.DTOs.filters.story_filter import StoryFilter


if TYPE_CHECKING:
    from ..models import Person


class StoryRepository(BaseRepository[Story, StoryFilter]):
    def __init__(self, session):
        super().__init__(session, Story)


    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: StoryFilter) -> Any:
        if filters.min_publication_date:
            statement = self._apply_min_publication_date(statement, filters.min_publication_date)

        if filters.max_publication_date:
            statement = self._apply_max_publication_date(statement, filters.max_publication_date)

        if filters.processed is not None:
            statement = self._apply_processed(statement, filters.processed)

        if filters.owner:
            statement = self._apply_owner(statement, filters.owner)

        return statement


    @staticmethod
    def _apply_min_publication_date(statement: Any, value: date) -> Any:
        return statement.where(Story.publication_date >= value)

    @staticmethod
    def _apply_max_publication_date(statement: Any, value: date) -> Any:
        return statement.where(Story.publication_date <= value)

    @staticmethod
    def _apply_processed(statement: Any, value: bool) -> Any:
        return statement.where(Story.processed == value)

    @staticmethod
    def _apply_owner(statement: Any, value: "Person") -> Any:
        return statement.where(Story.owner_id == value.id)