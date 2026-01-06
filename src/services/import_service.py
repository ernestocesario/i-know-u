from __future__ import annotations

import logging

from instamine.core import Instamine
from sqlmodel import Session

from src.config.app_properties import AppProperties
from src.repositories.person_repository import PersonRepository
from src.services.mappers.instamine_mapper import InstamineMapper
from src.services.storage.file_storage_manager import FileStorageManager


class ImportService:
    def __init__(self, session: Session, instamine_client: Instamine):
        self.session = session
        self.instamine = instamine_client

        self.logger = logging.getLogger(__name__)

        self.file_manager = FileStorageManager(base_root=AppProperties.CONTENTS_DIR)

        self.person_repository = PersonRepository(session)


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





