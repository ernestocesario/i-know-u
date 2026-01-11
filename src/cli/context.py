import logging
from typing import Optional

from instamine.core import Instamine
from instamine.providers import Provider1, Provider2

from src.config.app_properties import AppProperties
from src.config.rdb import create_db_and_tables, get_session
from src.repositories.content_repository import ContentRepository
from src.repositories.highlight_repository import HighlightRepository
from src.repositories.person_repository import PersonRepository
from src.repositories.post_repository import PostRepository
from src.repositories.story_repository import StoryRepository
from src.services.ai.providers.chroma_store import ChromaVectorStore
from src.services.ai.providers.gemini_provider import GeminiProvider
from src.services.content_processor_service import ContentProcessorService
from src.services.import_service import ImportService
from src.services.profile_query_service import ProfileQueryService
from src.services.removal_service import RemovalService
from src.services.storage.file_storage_manager import FileStorageManager


class CliContext:
    """
    Container for application state, database session, and service instances used throughout the CLI.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)


        # 1. Database Setup
        try:
            create_db_and_tables()
            self.logger.info("Database and tables checked/created.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize database: {e}")
            raise e
        self.session = get_session()


        # 2. Infrastructure Setup
        # File Manager
        self.file_manager = FileStorageManager(base_root=AppProperties.CONTENTS_DIR)

        # Vector Store
        self.vector_store = ChromaVectorStore(api_key=AppProperties.GOOGLE_AI_API_KEY)

        # AI Provider
        self.ai_provider = GeminiProvider(api_key=AppProperties.GOOGLE_AI_API_KEY)

        # Instamine client
        provider1 = Provider1()
        provider2 = Provider2()
        self.instamine_client = Instamine(
            provider1,
            provider2,
            early_init_providers=False,
            immediate_cleanup_provider=True
        )


        # 3. Services Initialization
        self.import_service = ImportService(
            session=self.session,
            instamine_client=self.instamine_client,
            vector_store=self.vector_store,
            file_manager=self.file_manager
        )

        self.removal_service = RemovalService(
            session=self.session,
            vector_store=self.vector_store,
            file_manager=self.file_manager
        )

        self.content_processor_service = ContentProcessorService(
            session=self.session,
            ai_provider=self.ai_provider,
            vector_store=self.vector_store,
            file_manager=self.file_manager
        )

        self.profile_query_service = ProfileQueryService(
            session=self.session,
            ai_provider=self.ai_provider,
            vector_store=self.vector_store
        )


        # 4. Repositories
        self.person_repository = PersonRepository(self.session)
        self.story_repository = StoryRepository(self.session)
        self.post_repository = PostRepository(self.session)
        self.highlight_repository = HighlightRepository(self.session)
        self.content_repository = ContentRepository(self.session)

        # 5. CLI State (Volatile state for navigation)
        self.current_username: Optional[str] = None
        self.current_person_id: Optional[int] = None



    def set_current_user(self, username: str):
        """Sets the context to a specific user after selection."""
        self.current_username = username
        person = self.person_repository.get_by_username(username)
        if person:
            self.current_person_id = person.id
        else:
            self.current_person_id = None



    def close(self):
        """Cleanup resources."""
        self.session.close()
        self.instamine_client.__exit__(None, None, None)