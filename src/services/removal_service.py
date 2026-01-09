from __future__ import annotations

import logging

from sqlmodel import Session

from src.config.app_properties import AppProperties
from src.models import Person
from src.models.DTOs.filters.sql_db.highlight_filter import HighlightFilter
from src.models.DTOs.filters.sql_db.post_filter import PostFilter
from src.models.DTOs.filters.sql_db.story_filter import StoryFilter
from src.models.utils.vector_object_type import VectorObjectType
from src.repositories.highlight_repository import HighlightRepository
from src.repositories.person_repository import PersonRepository
from src.repositories.post_repository import PostRepository
from src.repositories.story_repository import StoryRepository
from src.services.ai.interfaces.base_vector_store import BaseVectorStore
from src.services.storage.file_storage_manager import FileStorageManager


class RemovalService:
    def __init__(
            self,
            session: Session,
            vector_store: BaseVectorStore
    ):
        self.logger = logging.getLogger(__name__)

        self.session = session
        self.vector_store = vector_store

        self.file_manager = FileStorageManager(base_root=AppProperties.CONTENTS_DIR)

        self.person_repository = PersonRepository(session)
        self.post_repository = PostRepository(session)
        self.story_repository = StoryRepository(session)
        self.highlight_repository = HighlightRepository(session)


    # *******************************************************
    # Public methods
    # *******************************************************

    def remove_all_posts(self, username: str):
        person = self._get_person(username)

        try:
            # Get all posts by the person
            posts = self.post_repository.find(
                PostFilter(owner_is=person)
            )

            # Delete all posts in the relational database
            for post in posts:
                self.session.delete(post)

            # Delete all posts' content from storage
            self.file_manager.delete_posts_folder(person.external_id)

            # Delete all posts in the vector database
            self.vector_store.delete(person_id=person.id, object_type=VectorObjectType.POST)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error removing posts for user '{username}': {e}")
            raise e


    def remove_all_stories(self, username: str):
        person = self._get_person(username)

        try:
            # Get all stories by the person
            stories = self.story_repository.find(
                StoryFilter(owner_is=person)
            )

            # Delete all stories in the relational database
            for story in stories:
                self.session.delete(story)

            # Delete all stories' content from storage
            self.file_manager.delete_stories_folder(person.external_id)

            # Delete all stories in the vector database
            self.vector_store.delete(person_id=person.id, object_type=VectorObjectType.STORY)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error removing stories for user '{username}': {e}")
            raise e


    def remove_all_highlights(self, username: str):
        person = self._get_person(username)

        try:
            # Get all highlights by the person
            highlights = self.highlight_repository.find(
                HighlightFilter(owner_is=person)
            )

            # Delete all highlights in the relational database
            for highlight in highlights:
                self.session.delete(highlight)

            # Delete all highlights' content from storage
            self.file_manager.delete_highlights_folder(person.external_id)

            # Delete all posts in the vector database
            self.vector_store.delete(person_id=person.id, object_type=VectorObjectType.HIGHLIGHT)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error removing highlights for user '{username}': {e}")
            raise e


    def remove_person(self, username: str):
        person = self._get_person(username)
        external_id = person.external_id

        try:
            # Delete the person from the relational database
            self.session.delete(person)

            # Delete all user's content from storage
            self.file_manager.delete_user_folder(external_id)

            # Delete the person from the vector database
            self.vector_store.delete(person_id=person.id, object_type=None)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error removing person '{username}': {e}")
            raise e


    # *******************************************************
    # Private methods
    # *******************************************************

    def _get_person(self, username: str) -> Person:
        person = self.person_repository.get_by_username(username)

        if not person:
            raise ValueError(f"Person with username '{username}' not found.")

        return person