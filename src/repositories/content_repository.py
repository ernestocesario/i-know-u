from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING
from datetime import datetime
from sqlmodel import col, select

from .base_repository import BaseRepository
from ..models import Content
from src.models.DTOs.filters.sql_db.content_filter import ContentFilter

if TYPE_CHECKING:
    from ..models import Post, Highlight, Story, ContentAnalysis


class ContentRepository(BaseRepository[Content, ContentFilter]):
    def __init__(self, session):
        super().__init__(session, Content)


    # *******************************************************
    # Public methods
    # *******************************************************

    def get_by_external_id(self, external_id: str) -> Optional[Content]:
        statement = (
            select(Content)
            .where(Content.external_id == external_id)
        )

        return self.session.exec(statement).first()


    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: ContentFilter) -> Any:
        if filters.min_publication_datetime:
            statement = self._apply_min_publication_datetime(statement, filters.min_publication_datetime)

        if filters.max_publication_datetime:
            statement = self._apply_max_publication_datetime(statement, filters.max_publication_datetime)

        if filters.inferred_text_contains:
            statement = self._apply_inferred_text_contains(statement, filters.inferred_text_contains)

        if filters.processed_is is not None:
            statement = self._apply_processed_is(statement, filters.processed_is)

        if filters.post_is:
            statement = self._apply_post_is(statement, filters.post_is)

        if filters.highlight_is:
            statement = self._apply_highlight_is(statement, filters.highlight_is)

        if filters.story_is:
            statement = self._apply_story_is(statement, filters.story_is)

        if filters.content_analysis_is:
            statement = self._apply_content_analysis_is(statement, filters.content_analysis_is)

        return statement

    @staticmethod
    def _apply_min_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Content.publication_datetime >= value)

    @staticmethod
    def _apply_max_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Content.publication_datetime <= value)

    @staticmethod
    def _apply_inferred_text_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Content.inferred_text).ilike(f"%{value}%"))

    @staticmethod
    def _apply_processed_is(statement: Any, value: bool) -> Any:
        return statement.where(Content.processed == value)

    @staticmethod
    def _apply_post_is(statement: Any, value: Post) -> Any:
        return statement.where(Content.post_id == value.id)

    @staticmethod
    def _apply_highlight_is(statement: Any, value: Highlight) -> Any:
        return statement.where(Content.highlight_id == value.id)

    @staticmethod
    def _apply_story_is(statement: Any, value: Story) -> Any:
        return statement.where(Content.story_id == value.id)

    @staticmethod
    def _apply_content_analysis_is(statement: Any, value: ContentAnalysis) -> Any:
        return statement.where(Content.id == value.content_id)