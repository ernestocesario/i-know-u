from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING, Optional

from sqlmodel import col, select

from .base_repository import BaseRepository
from ..models import Post
from src.models.DTOs.filters.sql_db.post_filter import PostFilter

if TYPE_CHECKING:
    from ..models import Person


class PostRepository(BaseRepository[Post, PostFilter]):
    def __init__(self, session):
        super().__init__(session, Post)


    # *******************************************************
    # Public methods
    # *******************************************************

    def get_by_external_id(self, external_id: str) -> Optional[Post]:
        statement = (
            select(Post)
            .where(Post.external_id == external_id)
        )

        return self.session.exec(statement).first()


    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: PostFilter) -> Any:
        if filters.min_publication_datetime:
            statement = self._apply_min_publication_datetime(statement, filters.min_publication_datetime)

        if filters.max_publication_datetime:
            statement = self._apply_max_publication_datetime(statement, filters.max_publication_datetime)

        if filters.caption_contains:
            statement = self._apply_caption_contains(statement, filters.caption_contains)

        if filters.min_n_likes is not None:
            statement = self._apply_min_likes(statement, filters.min_n_likes)

        if filters.max_n_likes is not None:
            statement = self._apply_max_likes(statement, filters.max_n_likes)

        if filters.inference_summary_contains:
            statement = self._apply_inference_summary_contains(statement, filters.inference_summary_contains)

        if filters.owner_is:
            statement = self._apply_owner_is(statement, filters.owner_is)

        return statement


    @staticmethod
    def _apply_min_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Post.publication_datetime >= value)

    @staticmethod
    def _apply_max_publication_datetime(statement: Any, value: datetime) -> Any:
        return statement.where(Post.publication_datetime <= value)

    @staticmethod
    def _apply_caption_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Post.caption).ilike(f"%{value}%"))

    @staticmethod
    def _apply_min_likes(statement: Any, value: int) -> Any:
        return statement.where(Post.n_likes >= value)

    @staticmethod
    def _apply_max_likes(statement: Any, value: int) -> Any:
        return statement.where(Post.n_likes <= value)

    @staticmethod
    def _apply_inference_summary_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Post.inference_summary).ilike(f"%{value}%"))

    @staticmethod
    def _apply_owner_is(statement: Any, value: Person) -> Any:
        return statement.where(Post.owner_id == value.id)