import logging
from typing import List, Optional, Dict

from sqlmodel import Session

from src.models import Person, Content, Highlight, Post, Story
from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.DTOs.filters.sql_db.highlight_filter import HighlightFilter
from src.models.DTOs.filters.sql_db.person_filter import PersonFilter
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



    # *******************************************************
    # Public methods
    # *******************************************************

    # Method to check if a person is fully processed (profile, stories, posts, highlights)
    def is_fully_processed(self, person_id: int) -> bool:
        """
        Checks if a Person and all their associated content have been processed.
        """
        # 1. Fetch person
        person = self.person_repository.get_by_id(person_id)

        if not person:
            self.logger.error(f"Person with ID {person_id} not found.")
            raise ValueError(f"Person with ID {person_id} not found.")

        # 2. Check person profile info processing status
        if not person.processed:
            return False

        # 3. Check person's stories processing status
        unprocessed_stories = self.story_repository.find(
            StoryFilter(
                owner_is=person,
                processed_is=False
            )
        )
        if unprocessed_stories:
            return False

        # 4. Check person's posts processing status
        unprocessed_posts = self.post_repository.find(
            PostFilter(
                owner_is=person,
                processed_is=False
            )
        )
        if unprocessed_posts:
            return False

        # 5. Check person's highlights processing status
        unprocessed_highlights = self.highlight_repository.find(
            HighlightFilter(
                owner_is=person,
                processed_is=False
            )
        )
        if unprocessed_highlights:
            return False

        return True


    def process_profile_info(self, person_id: int) -> bool:
        """
        Analyzes the Person's raw metadata (Bio, Stats) to create a
        narrative description and indexes it as a PROFILE vector.
        """
        # 1. Fetch person
        person = self.person_repository.get_by_id(person_id)

        if not person:
            self.logger.error(f"Person with ID {person_id} not found.")
            raise ValueError(f"Person with ID {person_id} not found.")

        # 2. Check if already processed
        if person.processed:
            return False

        # 3. Process profile info
        try:
            stats = {
                "followers": person.n_followers,
                "following": person.n_following,
                "posts": person.n_posts,
            }

            person_inferred_text = self.ai_provider.enrich_profile(
                username=person.username,
                full_name=person.full_name,
                bio=person.bio,
                stats=stats
            )

            # 4. Update person entity
            person.inferred_text = person_inferred_text
            person.processed = True
            self.session.add(person)

            # 5. Update Vector Store
            self._index_profile_info(person)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error processing profile info for person ID {person.id}: {e}")
            raise e

        return True


    def process_stories(self, person_id: int) -> int:
        """
        Fetches unprocessed stories, runs AI analysis, updates SQL DB, and indexes to Vector Store.
        """
        person = self.person_repository.get_by_id(person_id)
        if not person:
            raise ValueError(f"Person with ID {person_id} not found.")

        unprocessed_stories = self.story_repository.find(
            StoryFilter(owner_is=person, processed_is=False)
        )

        if not unprocessed_stories:
            return 0

        processed_count = 0

        for story in unprocessed_stories:
            try:
                # 1. Validation
                if not story.content:
                    self.logger.warning(f"Story {story.id} has no content. Skipping.")
                    continue

                # 2. File Path Retrieval
                content_path = self.file_manager.get_story_filepath(
                    user_external_id=person.external_id,
                    story_external_id=story.external_id
                )

                # 3. AI Processing & SQL Persistence
                # Stories usually don't have captions in the same way posts do, so we pass None
                _, fresh_dto = self._process_and_save_content_ai(
                    content=story.content,
                    content_path=content_path,
                    caption=None
                )

                # 4. Finalize Story Entity
                story.processed = True
                self.session.add(story)

                # 5. Indexing (Delegated)
                self._index_story(story, fresh_dto=fresh_dto)

                # 6. Atomic Commit
                self.session.commit()
                processed_count += 1

            except Exception as e:
                self.session.rollback()
                self.logger.error(f"Error processing story {story.id}: {e}")

        return processed_count


    def process_posts(self, person_id: int) -> int:
        """
        Fetches unprocessed posts. For each post:
        1. Processes all child contents (Images/Videos).
        2. Generates a parent summary using AI.
        3. Indexes everything to Vector Store.
        """
        person = self.person_repository.get_by_id(person_id)
        if not person:
            raise ValueError(f"Person with ID {person_id} not found.")

        unprocessed_posts = self.post_repository.find(
            PostFilter(owner_is=person, processed_is=False)
        )

        if not unprocessed_posts:
            return 0

        processed_count = 0

        for post in unprocessed_posts:
            try:
                if not post.contents:
                    self.logger.warning(f"Post {post.id} has no contents. Skipping.")
                    continue

                content_descriptions: List[str] = []
                fresh_dtos_map: Dict[int, ContentAnalysisDTO] = {}
                post_caption = post.caption if post.caption else None

                # 1. Process Children (Contents)
                for content in post.contents:
                    content_path = self.file_manager.get_post_filepath(
                        user_external_id=person.external_id,
                        post_external_id=post.external_id,
                        content_external_id=content.external_id
                    )

                    text, dto = self._process_and_save_content_ai(
                        content=content,
                        content_path=content_path,
                        caption=post_caption
                    )

                    content_descriptions.append(text)
                    fresh_dtos_map[content.id] = dto

                # 2. Generate Parent Summary (Contextual)
                post_inference_summary = self.ai_provider.summarize_collection(
                    descriptions=content_descriptions,
                    caption=post_caption
                )
                post.inference_summary = post_inference_summary
                post.processed = True
                self.session.add(post)

                # 3. Indexing (Parent + Children)
                self._index_post(post, fresh_dtos_map=fresh_dtos_map)

                # 4. Atomic Commit
                self.session.commit()
                processed_count += 1

            except Exception as e:
                self.session.rollback()
                self.logger.error(f"Error processing post {post.id}: {e}")

        return processed_count


    def process_highlights(self, person_id: int) -> int:
        """
        Fetches unprocessed highlights. Similar flow to Posts.
        """
        person = self.person_repository.get_by_id(person_id)
        if not person:
            raise ValueError(f"Person with ID {person_id} not found.")

        unprocessed_highlights = self.highlight_repository.find(
            HighlightFilter(owner_is=person, processed_is=False)
        )

        if not unprocessed_highlights:
            return 0

        processed_count = 0

        for highlight in unprocessed_highlights:
            try:
                if not highlight.contents:
                    self.logger.warning(f"Highlight {highlight.id} has no contents. Skipping.")
                    continue

                content_descriptions: List[str] = []
                fresh_dtos_map: Dict[int, ContentAnalysisDTO] = {}

                # 1. Process Children (Contents)
                for content in highlight.contents:
                    content_path = self.file_manager.get_highlight_filepath(
                        user_external_id=person.external_id,
                        highlight_external_id=highlight.external_id,
                        content_external_id=content.external_id
                    )

                    # Highlights typically don't have a single caption per se,
                    # but we could pass the highlight title if needed. Here we pass None.
                    text, dto = self._process_and_save_content_ai(
                        content=content,
                        content_path=content_path,
                        caption=highlight.title
                    )

                    content_descriptions.append(text)
                    fresh_dtos_map[content.id] = dto

                # 2. Generate Parent Summary
                # We can include the Highlight Title as context for the summary
                highlight_summary = self.ai_provider.summarize_collection(
                    descriptions=content_descriptions,
                    caption=f"Highlight Title: {highlight.title}"
                )
                highlight.inference_summary = highlight_summary
                highlight.processed = True
                self.session.add(highlight)

                # 3. Indexing
                self._index_highlight(highlight, fresh_dtos_map=fresh_dtos_map)

                # 4. Atomic Commit
                self.session.commit()
                processed_count += 1

            except Exception as e:
                self.session.rollback()
                self.logger.error(f"Error processing highlight {highlight.id}: {e}")

        return processed_count


    def reintegrate_vector_db(self) -> None:
        """
        Wipes and Re-populates the Vector Store using existing data from SQL Database.
        This is a 'Free' operation (uses only embedding model, no Vision AI).
        Useful when changing embedding models or migrating data.
        """
        self.logger.info("Starting Vector DB Reintegration...")

        # 1. Clear existing vectors
        self.vector_store.clear_store()

        # 2. Re-index Profiles
        # (Assuming find() without args returns all, or implement get_all)
        profiles = self.person_repository.find(
            PersonFilter()
        )
        for person in profiles:
            self._index_profile(person)
        self.logger.info(f"Re-indexed {len(profiles)} profiles.")

        # 3. Re-index Stories
        stories = self.story_repository.find(
            StoryFilter()
        )
        for story in stories:
            if story.processed:
                # Passing None forces the indexer to fetch metadata from SQL
                self._index_story(story, fresh_dto=None)
        self.logger.info(f"Re-indexed {len(stories)} stories.")

        # 4. Re-index Posts
        posts = self.post_repository.find(
            PostFilter()
        )
        for post in posts:
            if post.processed:
                self._index_post(post, fresh_dtos_map=None)
        self.logger.info(f"Re-indexed {len(posts)} posts.")

        # 5. Re-index Highlights
        highlights = self.highlight_repository.find(
            HighlightFilter()
        )
        for hl in highlights:
            if hl.processed:
                self._index_highlight(hl, fresh_dtos_map=None)
        self.logger.info(f"Re-indexed {len(highlights)} highlights.")

        self.logger.info("Reintegration Complete.")



    # *******************************************************
    # Private Helper methods (AI & Persistence)
    # *******************************************************

    def _process_and_save_content_ai(
            self,
            content: Content,
            content_path: str,
            caption: Optional[str]
    ) -> tuple[str, ContentAnalysisDTO]:
        """
        Handles the expensive AI generation and SQL persistence for a single content item.
        Returns the generated text and the DTO for immediate indexing.
        """
        # Idempotency check: if already processed, return existing data
        if content.processed and content.inferred_text:
            # Reconstruct DTO from DB if possible, or return None (though usually not hit here)
            dto = ContentAnalysisDTO.from_entity(content.content_analysis)
            return content.inferred_text, dto

        # 1. AI: Textual Description
        content_inferred_text = self.ai_provider.get_content_description(
            file_path=content_path,
            mime_type=content.mime_type,
            caption=caption
        )

        # 2. AI: Structured Analysis
        content_analysis_dto = self.ai_provider.get_content_analysis(
            file_path=content_path,
            mime_type=content.mime_type,
            caption=caption
        )

        # 3. SQL Persistence
        content.inferred_text = content_inferred_text
        content.processed = True

        # Convert DTO to SQL Entity and link
        content_analysis = content_analysis_dto.to_entity(content_id=content.id)
        self.session.add(content_analysis)
        content.content_analysis = content_analysis

        self.session.add(content)

        # Note: We do NOT commit here. The caller handles the transaction scope.

        return content_inferred_text, content_analysis_dto



    # *******************************************************
    # Private Helper methods (Indexing Logic)
    # *******************************************************

    def _index_profile(self, person: Person) -> None:
        """
        Indexes the Person Profile.
        """
        if not person.inferred_text:
            return

        try:
            vector_doc = VectorDocumentDTO(
                text=person.inferred_text,
                person_id=person.id,
                object_type=VectorObjectType.PROFILE,
                object_id=person.id,
                mime_type="text/plain",
                content_analysis_dto=None
            )
            self.vector_store.add_document(vector_doc)
        except Exception as e:
            self.logger.error(f"Failed to index profile for user '{person.username}': {e}")


    def _index_content(
            self,
            person_id: int,
            content: Content,
            parent_object_id: int,
            parent_type: VectorObjectType,
            fresh_analysis_dto: Optional[ContentAnalysisDTO] = None
    ) -> None:
        """
        Core Indexing Logic for a single Content item.
        Handles both Fresh Indexing (dto provided) and Reintegration (dto fetched from DB).
        """
        if not content.inferred_text:
            return

        # 1. Determine Analysis Source
        final_dto = fresh_analysis_dto

        # Reintegration scenario: Restore from SQL using the factory method
        if final_dto is None and content.content_analysis:
            final_dto = ContentAnalysisDTO.from_entity(content.content_analysis)

        # 2. Create Vector Document
        vector_doc = VectorDocumentDTO(
            text=content.inferred_text,
            person_id=person_id,
            object_id=parent_object_id,
            object_type=parent_type,
            mime_type=content.mime_type,
            content_analysis_dto=final_dto
        )

        # 3. Push to Vector Store
        self.vector_store.add_document(vector_doc)


    def _index_profile_info(self, person: Person) -> None:
        """
        Helper method to create the VectorDocumentDTO for a Person's profile
        and add it to the Vector Store.
        Used both in initial processing and during restoration/re-indexing.
        """
        if not person.inferred_text:
            return

        try:
            vector_doc = VectorDocumentDTO(
                text=person.inferred_text,
                person_id=person.id,
                object_type=VectorObjectType.PROFILE,
                object_id=person.id,
                mime_type="text/plain",
                content_analysis_dto=None
            )

            self.vector_store.add_document(vector_doc)

        except Exception as e:
            self.logger.error(f"Failed to index profile for user '{person.username}': {e}")
            raise e


    def _index_story(self, story: Story, fresh_dto: Optional[ContentAnalysisDTO] = None) -> None:
        """
        Indexes a Story.
        """
        if not story.content:
            return

        self._index_content(
            person_id=story.owner_id,
            content=story.content,
            parent_object_id=story.id,
            parent_type=VectorObjectType.STORY,
            fresh_analysis_dto=fresh_dto
        )


    def _index_post(self, post: Post, fresh_dtos_map: Optional[Dict[int, ContentAnalysisDTO]] = None) -> None:
        """
        Indexes a Post (Summary + All Contents).
        """
        # 1. Index Summary (Parent)
        if post.inference_summary:
            summary_doc = VectorDocumentDTO(
                text=post.inference_summary,
                person_id=post.owner_id,
                object_id=post.id,
                object_type=VectorObjectType.POST,
                mime_type="text/plain",
                content_analysis_dto=None  # Summaries don't have structured analysis
            )
            self.vector_store.add_document(summary_doc)

        # 2. Index Children (Contents)
        if post.contents:
            for content in post.contents:
                # Retrieve specific DTO if we are in fresh processing
                specific_dto = fresh_dtos_map.get(content.id) if fresh_dtos_map else None

                self._index_content(
                    person_id=post.owner_id,
                    content=content,
                    parent_object_id=post.id,
                    parent_type=VectorObjectType.POST_CONTENT,
                    fresh_analysis_dto=specific_dto
                )


    def _index_highlight(self, highlight: Highlight,
                         fresh_dtos_map: Optional[Dict[int, ContentAnalysisDTO]] = None) -> None:
        """
        Indexes a Highlight (Summary + All Contents).
        """
        # 1. Index Summary (Parent)
        if highlight.inference_summary:
            summary_doc = VectorDocumentDTO(
                text=highlight.inference_summary,
                person_id=highlight.owner_id,
                object_id=highlight.id,
                object_type=VectorObjectType.HIGHLIGHT,
                mime_type="text/plain",
                content_analysis_dto=None
            )
            self.vector_store.add_document(summary_doc)

        # 2. Index Children (Contents)
        if highlight.contents:
            for content in highlight.contents:
                specific_dto = fresh_dtos_map.get(content.id) if fresh_dtos_map else None

                self._index_content(
                    person_id=highlight.owner_id,
                    content=content,
                    parent_object_id=highlight.id,
                    parent_type=VectorObjectType.HIGHLIGHT_CONTENT,
                    fresh_analysis_dto=specific_dto
                )