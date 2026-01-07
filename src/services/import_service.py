from __future__ import annotations

import logging
from typing import Optional, List

from instamine.core import Instamine
from sqlmodel import Session

from src.config.app_properties import AppProperties
from src.repositories.content_repository import ContentRepository
from src.repositories.highlight_repository import HighlightRepository
from src.repositories.person_repository import PersonRepository
from src.repositories.post_repository import PostRepository
from src.repositories.story_repository import StoryRepository
from src.services.mappers.instamine_mapper import InstamineMapper
from src.services.storage.file_storage_manager import FileStorageManager


class ImportService:
    def __init__(self, session: Session, instamine_client: Instamine):
        self.session = session
        self.instamine = instamine_client

        self.logger = logging.getLogger(__name__)

        self.file_manager = FileStorageManager(base_root=AppProperties.CONTENTS_DIR)

        self.person_repository = PersonRepository(session)
        self.post_repository = PostRepository(session)
        self.story_repository = StoryRepository(session)
        self.highlight_repository = HighlightRepository(session)
        self.content_repository = ContentRepository(session)


    def import_profile_metadata(self, target_username: str) -> None:
        try:
            profile_dto = self.instamine.get_profile_info(username=target_username)
        except Exception as e:
            self.logger.error(f"Failed to fetch profile info for '{target_username}': {e}")
            raise e

        tmp_person = InstamineMapper.to_person_entity(profile_dto)

        existing_person = self.person_repository.get_by_external_id(tmp_person.external_id)

        if existing_person:
            update_data = tmp_person.model_dump(exclude_none=True, exclude={"id"})

            existing_person.sqlmodel_update(update_data)

            person_to_save = existing_person
        else:
            self.session.add(tmp_person)
            person_to_save = tmp_person

        self.session.commit()
        self.session.refresh(person_to_save)


    def import_posts(self, target_username: str, limit: int) -> None:
        person = self.person_repository.get_by_username(username=target_username)

        # 1. Verify that the person exists in the database
        if not person:
            self.logger.error(f"Person with username '{target_username}' not found in the database.")
            raise ValueError(f"Person with username '{target_username}' not found in the database.")

        # 2. Fetch posts from Instamine
        try:
            post_dtos = self.instamine.get_posts(username=target_username, limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to fetch posts for '{target_username}': {e}")
            raise e

        # 3. Process and store each post
        for post_dto in post_dtos:
            # A. Check if the post already exists
            existing_post = self.post_repository.get_by_external_id(post_dto.id)
            if existing_post:
                continue

            # B. Save post
            try:
                # Map PostDTO to Post entity
                post_entity = InstamineMapper.to_post_entity(post_dto, owner=person)
                self.session.add(post_entity)

                # Process and store each content
                for content_dto in post_dto.contents:

                    # Check content data
                    content_data = content_dto.read()
                    if not content_data:
                        self.logger.warning(f"Content data for content ID '{content_dto.id}' is empty.")
                        continue

                    # Map ContentDTO to Content entity
                    content_entity = InstamineMapper.to_content_entity(content_dto)

                    # Link content to post
                    content_entity.post = post_entity

                    # Save content file
                    self.file_manager.save_post_media(
                        user_id=person.external_id,
                        post_id=post_entity.external_id,
                        content_id=content_dto.id,
                        data=content_data,
                        mime_type=content_dto.mime_type
                    )

                    self.session.add(content_entity)

                self.session.commit()

            except Exception as e:
                self.logger.error(f"Failed to import post '{post_dto.id}': {e}")
                self.session.rollback()
                continue


    def import_stories(self, target_username: str, limit: int) -> None:
        person = self.person_repository.get_by_username(username=target_username)

        # 1. Verify that the person exists in the database
        if not person:
            self.logger.error(f"Person with username '{target_username}' not found in the database.")
            raise ValueError(f"Person with username '{target_username}' not found in the database.")

        # 2. Fetch stories from Instamine
        try:
            story_dtos = self.instamine.get_stories(username=target_username, limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to fetch stories for '{target_username}': {e}")
            raise e

        # 3. Process and store each story
        for story_dto in story_dtos:
            # A. Check if the story already exists
            existing_story = self.story_repository.get_by_external_id(story_dto.id)
            if existing_story:
                continue

            # B. Save story
            try:
                # Map StoryDTO to Story entity
                story_entity = InstamineMapper.to_story_entity(story_dto, owner=person)
                self.session.add(story_entity)

                # Process and store the content
                content_dto = story_dto.content

                if not content_dto or not content_dto.size:
                    raise ValueError(f"Story '{story_dto.id}' has no valid content to import.")

                # Map ContentDTO to Content entity
                content_entity = InstamineMapper.to_content_entity(content_dto)

                # Link content to story
                content_entity.story = story_entity

                # Save content file
                content_data = content_dto.read()

                self.file_manager.save_story_media(
                    user_id=person.external_id,
                    story_id=story_entity.external_id,
                    data=content_data,
                    mime_type=content_dto.mime_type
                )

                self.session.add(content_entity)
                self.session.commit()
            except Exception as e:
                self.logger.error(f"Failed to import story '{story_dto.id}': {e}")
                self.session.rollback()
                continue


    def get_highlights_titles(self, target_username: str) -> list[str]:
        try:
            return self.instamine.get_highlights_titles(username=target_username)
        except Exception as e:
            self.logger.error(f"Failed to fetch highlights titles for '{target_username}': {e}")
            raise e


    def import_highlights(self, target_username: str, limit: int, highlight_titles: Optional[List[str]] = None) -> None:
        person = self.person_repository.get_by_username(username=target_username)

        # 1. Verify that the person exists in the database
        if not person:
            self.logger.error(f"Person with username '{target_username}' not found in the database.")
            raise ValueError(f"Person with username '{target_username}' not found in the database.")

        # 2. Check highlight titles
        if not highlight_titles:
            highlight_titles = self.get_highlights_titles(target_username=target_username)

        # 3. Fetch highlights from Instamine
        for title in highlight_titles:
            try:
                # A. Fetch highlight using its title
                highlight_dto = self.instamine.get_highlight_by_title(
                    username=target_username,
                    title=title,
                    limit=limit
                )

                # B. Map HighlightDTO to Highlight entity
                tmp_highlight = InstamineMapper.to_highlight_entity(highlight_dto, owner=person)

                # C. Check if the highlight already exists, if so, update it, otherwise create new
                existing_highlight = self.highlight_repository.get_by_external_id(tmp_highlight.external_id)
                if existing_highlight:
                    update_data = tmp_highlight.model_dump(exclude_none=True, exclude={'id', 'external_id', 'owner_id', 'owner'})
                    existing_highlight.sqlmodel_update(update_data)

                    current_highlight = existing_highlight
                else:
                    self.session.add(tmp_highlight)
                    current_highlight = tmp_highlight

                # D. Manage highlight contents
                for content_dto in highlight_dto.contents:
                    # Check if the content already exists, if so, skip it
                    existing_content = self.content_repository.get_by_external_id(content_dto.id)
                    if existing_content:
                        continue

                    # Process new content

                    # Check content data
                    if not content_dto.size:
                        raise ValueError(f"Highlight '{highlight_dto.id}' has no valid content to import.")

                    # Map ContentDTO to Content entity
                    content_entity = InstamineMapper.to_content_entity(content_dto)
                    content_entity.highlight = current_highlight

                    # Save content file
                    content_data = content_dto.read()
                    self.file_manager.save_highlight_media(
                        user_id=person.external_id,
                        highlight_id=current_highlight.external_id,
                        content_id=content_dto.id,
                        data=content_data,
                        mime_type=content_dto.mime_type
                    )

                    self.session.add(content_entity)

                # E. Commit all changes
                self.session.commit()

            except Exception as e:
                self.logger.error(f"Failed to import highlight '{title}': {e}")
                self.session.rollback()
                continue

