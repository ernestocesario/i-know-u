from __future__ import annotations

import logging

from instamine.core import Instamine
from sqlmodel import Session

from src.config.app_properties import AppProperties
from src.repositories.person_repository import PersonRepository
from src.repositories.post_repository import PostRepository
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
                post_entity = InstamineMapper.to_post_entity(post_dto, owner_id=person.id)
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
                        username=target_username,
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