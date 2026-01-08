from __future__ import annotations

from typing import Any, TYPE_CHECKING
from datetime import datetime
from sqlmodel import col

from .base_repository import BaseRepository
from ..models import Comment
from src.models.DTOs.filters.sql_db.comment_filter import CommentFilter

if TYPE_CHECKING:
    from ..models import Post


class CommentRepository(BaseRepository[Comment, CommentFilter]):
    def __init__(self, session):
        super().__init__(session, Comment)


    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: CommentFilter) -> Any:
        if filters.min_publication_datetime:
            statement = self._apply_min_publication_datetime(statement, filters.min_publication_datetime)

        if filters.max_publication_datetime:
            statement = self._apply_max_publication_datetime(statement, filters.max_publication_datetime)

        if filters.text_contains:
            statement = self._apply_text_contains(statement, filters.text_contains)

        if filters.post_is:
            statement = self._apply_post_is(statement, filters.post_is)

        return statement


    @staticmethod
    def _apply_min_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Comment.publication_datetime >= value)

    @staticmethod
    def _apply_max_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Comment.publication_datetime <= value)

    @staticmethod
    def _apply_text_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Comment.text).ilike(f"%{value}%"))

    @staticmethod
    def _apply_post_is(statement: Any, post: Post) -> Any:
        return statement.where(Comment.post_id == post.id)