from typing import Optional, Any

from sqlmodel import select, col

from .base_repository import BaseRepository
from ..models import Person
from src.models.DTOs.filters.sql_db.person_filter import PersonFilter


class PersonRepository(BaseRepository[Person, PersonFilter]):
    def __init__(self, session):
        super().__init__(session, Person)


    # *******************************************************
    # Public methods
    # *******************************************************

    def get_by_external_id(self, external_id: str) -> Optional[Person]:
        statement = (
            select(Person)
            .where(Person.external_id == external_id)
        )

        return self.session.exec(statement).first()


    def get_by_username(self, username: str) -> Optional[Person]:
        statement = (
            select(Person)
            .where(Person.username == username)
        )

        return self.session.exec(statement).first()


    def get_by_full_name(self, full_name: str) -> Optional[Person]:
        statement = (
            select(Person)
            .where(Person.full_name == full_name)
        )

        return self.session.exec(statement).first()



    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: PersonFilter) -> Any:
        if filters.username_contains:
            statement = self._apply_username_contains(statement, filters.username_contains)

        if filters.full_name_contains:
            statement = self._apply_full_name_contains(statement, filters.full_name_contains)

        if filters.bio_contains:
            statement = self._apply_bio_contains(statement, filters.bio_contains)

        if filters.min_n_followers is not None:
            statement = self._apply_min_followers(statement, filters.min_n_followers)

        if filters.max_n_followers is not None:
            statement = self._apply_max_followers(statement, filters.max_n_followers)

        if filters.min_n_following is not None:
            statement = self._apply_min_following(statement, filters.min_n_following)

        if filters.max_n_following is not None:
            statement = self._apply_max_following(statement, filters.max_n_following)

        if filters.min_n_posts is not None:
            statement = self._apply_min_posts(statement, filters.min_n_posts)

        if filters.max_n_posts is not None:
            statement = self._apply_max_posts(statement, filters.max_n_posts)

        return statement


    @staticmethod
    def _apply_username_contains( statement: Any, value: str) -> Any:
        return statement.where(col(Person.username).ilike(f"%{value}%"))

    @staticmethod
    def _apply_full_name_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Person.full_name).ilike(f"%{value}%"))

    @staticmethod
    def _apply_bio_contains(statement: Any, value: str) -> Any:
        return statement.where(col(Person.bio).ilike(f"%{value}%"))

    @staticmethod
    def _apply_min_followers(statement: Any, value: int) -> Any:
        return statement.where(Person.n_followers >= value)

    @staticmethod
    def _apply_max_followers(statement: Any, value: int) -> Any:
        return statement.where(Person.n_followers <= value)

    @staticmethod
    def _apply_min_following(statement: Any, value: int) -> Any:
        return statement.where(Person.n_following >= value)

    @staticmethod
    def _apply_max_following(statement: Any, value: int) -> Any:
        return statement.where(Person.n_following <= value)

    @staticmethod
    def _apply_min_posts(statement: Any, value: int) -> Any:
        return statement.where(Person.n_posts >= value)

    @staticmethod
    def _apply_max_posts(statement: Any, value: int) -> Any:
        return statement.where(Person.n_posts <= value)