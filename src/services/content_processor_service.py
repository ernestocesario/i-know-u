import logging

from sqlmodel import Session

from src.models import Person, Content
from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.DTOs.filters.sql_db.story_filter import StoryFilter
from src.models.DTOs.vector_document_dto import VectorDocumentDTO
from src.models.utils.vector_object_type import VectorObjectType
from src.repositories.person_repository import PersonRepository
from src.repositories.story_repository import StoryRepository
from src.services.ai.interfaces.base_ai_provider import BaseAIProvider
from src.services.ai.interfaces.base_vector_store import BaseVectorStore
from src.services.storage.file_storage_manager import FileStorageManager


class ContentProcessorService:
    def __init__(
            self,
            session: Session,
            ai_provider: BaseAIProvider,
            vector_store: BaseVectorStore,
            file_manager: FileStorageManager
    ):
        self.logger = logging.getLogger(__name__)

        self.session = session
        self.ai_provider = ai_provider
        self.vector_store = vector_store
        self.file_manager = file_manager

        self.person_repository = PersonRepository(session)
        self.story_repository = StoryRepository(session)


    # TODO add process_person_metadata method, and add VectorObjectType .PERSON_METADATA

    # *******************************************************
    # Public methods
    # *******************************************************

    def process_stories(self, person_id: int) -> int:
        """
        Fetches unprocessed stories, runs AI analysis, updates SQL DB and Vector Store.
        """
        # 1. Fetch person
        person = self.person_repository.get_by_id(person_id)
        if not person:
            self.logger.error(f"Person with ID {person_id} not found.")
            return 0

        # 2. Fetch unprocessed stories
        unprocessed_stories = self.story_repository.find(
            StoryFilter(
                owner_is=person,
                processed=False
            )
        )

        if not unprocessed_stories:
            return 0

        processed_count = 0

        for story in unprocessed_stories:
            try:
                # A. File path retrival for story content
                content_path = self.file_manager.get_story_path(
                    user_external_id=person.external_id,
                    story_external_id=story.external_id
                )

                # B. Content analysis via AI provider
                self._process_single_content(
                    person=person,
                    content=story.content,
                    content_path=content_path,
                    vector_object_id=story.id,
                    vector_object_type=VectorObjectType.STORY
                )

                story.processed = True
                self.session.add(story)
                self.session.commit()

                processed_count += 1

            except Exception as e:
                self.session.rollback()
                self.logger.error(f"Error processing story ID {story.id}: {e}")

        return processed_count



    # *******************************************************
    # Private methods
    # *******************************************************

    def _process_single_content(
            self,
            person: Person,
            content: Content,
            content_path: str,
            vector_object_id: int,
            vector_object_type: VectorObjectType
    ) -> str:
        content_inferred_text = self.ai_provider.get_content_description(
            file_path=content_path,
            mime_type=content.mime_type
        )

        content_analysis_dto: ContentAnalysisDTO = self.ai_provider.get_content_analysis(
            file_path=content_path,
            mime_type=content.mime_type
        )

        # C. Update content and analysis in DB
        content.inferred_text = content_inferred_text
        content.processed = True

        content_analysis = content_analysis_dto.to_entity(content_id=content.id)
        self.session.add(content_analysis)
        content.content_analysis = content_analysis

        self.session.add(content)

        # D. Update Vector Store
        vector_doc = VectorDocumentDTO(
            text=content_inferred_text,
            person_id=person.id,
            object_type=vector_object_type,
            object_id=vector_object_id,
            mime_type=content.mime_type,
            content_analysis_dto=content_analysis_dto
        )
        self.vector_store.add_document(vector_doc)

        return content_inferred_text