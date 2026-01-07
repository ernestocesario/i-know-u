from __future__ import annotations

import logging

from sqlmodel import Session

from src.config.app_properties import AppProperties
from src.models import Person
from src.models.DTOs.filters.highlight_filter import HighlightFilter
from src.models.DTOs.filters.post_filter import PostFilter
from src.models.DTOs.filters.story_filter import StoryFilter
from src.repositories.highlight_repository import HighlightRepository
from src.repositories.person_repository import PersonRepository
from src.repositories.post_repository import PostRepository
from src.repositories.story_repository import StoryRepository
from src.services.storage.file_storage_manager import FileStorageManager


class RemovalService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

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

            # Delete all posts in the database
            for post in posts:
                self.session.delete(post)

            # Delete all posts' content from storage
            self.file_manager.delete_posts_folder(person.external_id)

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

            # Delete all stories in the database
            for story in stories:
                self.session.delete(story)

            # Delete all stories' content from storage
            self.file_manager.delete_stories_folder(person.external_id)

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

            # Delete all highlights in the database
            for highlight in highlights:
                self.session.delete(highlight)

            # Delete all highlights' content from storage
            self.file_manager.delete_highlights_folder(person.external_id)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error removing highlights for user '{username}': {e}")
            raise e


    def remove_person(self, username: str):
        person = self._get_person(username)
        external_id = person.external_id

        try:
            # Delete the person from the database
            self.session.delete(person)

            # Delete all user's content from storage
            self.file_manager.delete_user_folder(external_id)

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