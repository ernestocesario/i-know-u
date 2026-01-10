import logging

from sqlmodel import Session

from src.models.DTOs.filters.vector_db.vector_filter import VectorFilter
from src.repositories.person_repository import PersonRepository
from src.services.ai.interfaces.base_ai_provider import BaseAIProvider
from src.services.ai.interfaces.base_vector_store import BaseVectorStore


class ProfileQueryService:
    def __init__(
            self,
            session: Session,
            ai_provider: BaseAIProvider,
            vector_store: BaseVectorStore
    ):
        self.logger = logging.getLogger(__name__)

        self.session = session
        self.ai_provider = ai_provider
        self.vector_store = vector_store

        self.person_repository = PersonRepository(session)


    def ask_question_about_profile(self, username: str, question: str, k: int = 15) -> str:
        """
        Answers a question about a specific user profile using RAG.

        Args:
            username: The username of the person whose profile is being queried.
            question: The natural language question (e.g., "What is their favorite food?").
            k: Number of relevant context chunks to retrieve (default 15).

        Returns:
            The AI-generated answer based on the retrieved content.
        """
        # 1. Retrieve the person by username
        person = self.person_repository.get_by_username(username)
        if not person:
            raise ValueError(f"Person with username '{username}' not found.")

        try:
            # 2. Build vector filter to scope search to this person
            vector_filter = VectorFilter(
                person_id=person.id,
            )

            # 3. Search vector store for relevant documents
            relevant_docs = self.vector_store.search(
                query=question,
                filters=vector_filter,
                k=k,
            )

            if not relevant_docs:
                return "I couldn't find any relevant information in the user's content to answer your question."

            # 4. Use AI provider to generate answer based on retrieved documents
            context_block = "\n\n".join(relevant_docs)

            answer = self.ai_provider.generate_response(
                context=context_block,
                question=question
            )

            return answer
        except Exception as e:
            self.logger.error(f"Error answering question about profile '{username}': {e}")
            raise e