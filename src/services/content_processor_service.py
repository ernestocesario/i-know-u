import logging
from typing import List

from sqlmodel import Session

from src.models import Person, Content
from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.DTOs.filters.sql_db.highlight_filter import HighlightFilter
from src.models.DTOs.filters.sql_db.post_filter import PostFilter
from src.models.DTOs.filters.sql_db.story_filter import StoryFilter
from src.models.DTOs.vector_document_dto import VectorDocumentDTO
from src.models.utils.vector_object_type import VectorObjectType
from src.repositories.highlight_repository import HighlightRepository
from src.repositories.person_repository import PersonRepository
from src.repositories.post_repository import PostRepository
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
        self.post_repository = PostRepository(session)
        self.highlight_repository = HighlightRepository(session)


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
            raise ValueError(f"Person with ID {person_id} not found.")

        # 2. Fetch unprocessed stories
        unprocessed_stories = self.story_repository.find(
            StoryFilter(
                owner_is=person,
                processed_is=False
            )
        )

        if not unprocessed_stories:
            return 0

        processed_count = 0

        # 3. Process each unprocessed story
        for story in unprocessed_stories:
            try:
                # A. File path retrival for story content
                content_path = self.file_manager.get_story_filepath(
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


    def process_posts(self, person_id: int) -> int:
        """
        Fetches unprocessed stories, runs AI analysis, updates SQL DB and Vector Store.
        """
        # 1. Fetch person
        person = self.person_repository.get_by_id(person_id)

        if not person:
            self.logger.error(f"Person with ID {person_id} not found.")
            raise ValueError(f"Person with ID {person_id} not found.")

        # 2. Fetch unprocessed posts
        unprocessed_posts = self.post_repository.find(
            PostFilter(
                owner_is=person,
                processed_is=False
            )
        )

        if not unprocessed_posts:
            return 0

        processed_count = 0

        # 3. Process each unprocessed post
        for post in unprocessed_posts:
            try:
                if not post.contents:
                    raise ValueError(f"Post ID {post.id} has no associated contents.")

                content_descriptions: List[str] = []

                # A. Process each content in the post
                for content in post.contents:
                    # A.1 File path retrieval for post content
                    content_path = self.file_manager.get_post_filepath(
                        user_external_id=person.external_id,
                        post_external_id=post.external_id,
                        content_external_id=content.external_id
                    )

                    # A.2 Process content
                    content_description = self._process_single_content(
                        person=person,
                        content=content,
                        content_path=content_path,
                        vector_object_id=content.id,
                        vector_object_type=VectorObjectType.POST
                    )

                    content_descriptions.append(content_description)

                # B. Generate post summary from content descriptions
                post_inferred_summary = self.ai_provider.summarize_collection(content_descriptions)
                post.inferred_summary = post_inferred_summary

                summary_doc = VectorDocumentDTO(
                    text=post_inferred_summary,
                    person_id=person.id,
                    object_type=VectorObjectType.POST,
                    object_id=post.id,
                    mime_type="text/plain",
                    content_analysis_dto=None
                )
                self.vector_store.add_document(summary_doc)

                post.processed = True
                self.session.add(post)
                self.session.commit()
                processed_count += 1
            except Exception as e:
                self.session.rollback()
                self.logger.error(f"Error processing post ID {post.id}: {e}")
        return processed_count


    def process_highlights(self, person_id: int) -> int:
        """
        Fetches unprocessed highlights, runs AI analysis, updates SQL DB and Vector Store.
        """
        # 1. Fetch person
        person = self.person_repository.get_by_id(person_id)
        if not person:
            self.logger.error(f"Person with ID {person_id} not found.")
            raise ValueError(f"Person with ID {person_id} not found.")

        # 2. Fetch unprocessed highlights
        unprocessed_highlights = self.highlight_repository.find(
            HighlightFilter(
                owner_is=person,
                processed_is=False
            )
        )

        if not unprocessed_highlights:
            return 0

        processed_count = 0

        # 3. Process each unprocessed highlight
        for highlight in unprocessed_highlights:
            try:
                if not highlight.contents:
                    raise ValueError(f"Highlight ID {highlight.id} has no associated contents.")

                content_descriptions: List[str] = []

                # A. Process each content in the post
                for content in highlight.contents:
                    # A.1 File path retrieval for highlight content
                    content_path = self.file_manager.get_highlight_filepath(
                        user_external_id=person.external_id,
                        highlight_external_id=highlight.external_id,
                        content_external_id=content.external_id
                    )

                    # A.2 Process content
                    content_description = self._process_single_content(
                        person=person,
                        content=content,
                        content_path=content_path,
                        vector_object_id=content.id,
                        vector_object_type=VectorObjectType.HIGHLIGHT
                    )

                    content_descriptions.append(content_description)

                # B. Generate highlight summary from content descriptions
                highlight_inferred_summary = self.ai_provider.summarize_collection(content_descriptions)
                highlight.inferred_summary = highlight_inferred_summary

                summary_doc = VectorDocumentDTO(
                    text=highlight_inferred_summary,
                    person_id=person.id,
                    object_type=VectorObjectType.HIGHLIGHT,
                    object_id=highlight.id,
                    mime_type="text/plain",
                    content_analysis_dto=None
                )
                self.vector_store.add_document(summary_doc)

                highlight.processed = True
                self.session.add(highlight)
                self.session.commit()
                processed_count += 1
            except Exception as e:
                self.session.rollback()
                self.logger.error(f"Error processing highlight ID {highlight.id}: {e}")
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
        # Important because a content can be associated to multiple objects (e.g. multiple stories and multiple highlights)
        if content.processed:
            return content.inferred_text

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