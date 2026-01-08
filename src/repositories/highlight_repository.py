from __future__ import annotations

from typing import Any, TYPE_CHECKING, Optional
from sqlmodel import col, select

from .base_repository import BaseRepository
from ..models import Highlight
from src.models.DTOs.filters.sql_db.highlight_filter import HighlightFilter

if TYPE_CHECKING:
    from ..models import Person


class HighlightRepository(BaseRepository[Highlight, HighlightFilter]):
    def __init__(self, session):
        super().__init__(session, Highlight)


    # *******************************************************
    # Public methods
    # *******************************************************

    def get_by_external_id(self, external_id: str) -> Optional[Highlight]:
        statement = (
            select(Highlight)
            .where(Highlight.external_id == external_id)
        )

        return self.session.exec(statement).first()


    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: HighlightFilter) -> Any:
        if filters.title_contains:
            statement = self._apply_title_contains(statement, filters.title_contains)

        if filters.inference_summary_contains:
            statement = self._apply_inference_summary_contains(statement, filters.inference_summary_contains)

        if filters.owner_is:
            statement = self._apply_owner_is(statement, filters.owner_is)

        return statement


    @staticmethod
    def _apply_title_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Highlight.title).ilike(f"%{value}%"))

    @staticmethod
    def _apply_inference_summary_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Highlight.inference_summary).ilike(f"%{value}%"))

    @staticmethod
    def _apply_owner_is(statement: Any, owner: Person) -> Any:
        return statement.where(Highlight.owner_id == owner.id)