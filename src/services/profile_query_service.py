import logging

from sqlmodel import Session

from src.models.DTOs.filters.vector_db.vector_filter import VectorFilter
from src.models.DTOs.query_intent_dto import QueryIntentDTO
from src.models.utils.vector_object_type import VectorObjectType
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


    def ask_question_about_profile(self, username: str, question: str, k: int = 15, self_querying_retrieval: bool = False) -> str:
        """
        Answers a question about a specific user profile using RAG.

        Args:
            username: The username of the person whose profile is being queried.
            question: The natural language question (e.g., "What is their favorite food?"). If the question starts with "@", self-querying retrieval is disabled.
            k: Number of relevant context chunks to retrieve (default 15).
            self_querying_retrieval: refines the search using filters extracted from the query; if disabled, it performs a basic search without filters.
        Returns:
            The AI-generated answer based on the retrieved content.
        """
        if not k or k <= 0:
            raise ValueError("Parameter 'k' must be a positive integer.")

        # 1. Check for self-querying retrieval flag (indicated by "@" prefix)
        if question.startswith("@"):
            self.logger.info("Self-querying retrieval disabled manually via '@' prefix in question.")
            self_querying_retrieval = False
            question = question[1:].strip()

        # 2. Retrieve the person by username
        person = self.person_repository.get_by_username(username)
        if not person:
            raise ValueError(f"Person with username '{username}' not found.")

        try:
            # 3. Extract search intent and filters from the question using AI provider if self-querying retrieval is enabled;
            # otherwise, use the raw question as the semantic query with no filters.
            query_intent = QueryIntentDTO(filters=None)

            if self_querying_retrieval:
                query_intent = self.ai_provider.extract_search_intent(question)
                self.logger.info(f"Extracted Filters: {query_intent.filters}")

            # 4. Query building
            # Base filter
            base_filter = VectorFilter(person_id=person.id)
            final_query_node = base_filter

            # If filters are extracted from the query, build a hybrid filter logic
            if query_intent.filters:
                # A. Strict Match
                strict_filter = VectorFilter(content_analysis_dto=query_intent.filters)

                # B. Context Match
                context_filter = (
                        VectorFilter(object_type=VectorObjectType.PROFILE) |
                        VectorFilter(object_type=VectorObjectType.POST) |
                        VectorFilter(object_type=VectorObjectType.HIGHLIGHT)
                )

                # C. Union: (Strict) OR (Context)
                hybrid_logic = strict_filter | context_filter

                # D. Final: PersonID AND (Hybrid)
                final_query_node = base_filter & hybrid_logic


            # 5. Search vector store for relevant documents
            relevant_docs = self.vector_store.search(
                query=question,
                filters=final_query_node.build(),
                k=k,
            )

            # 6. If no relevant documents found and filters were applied, retry without filters to avoid over-filtering
            if not relevant_docs:
                self.logger.info("No relevant documents found")

                if query_intent.filters:
                    self.logger.info("Retrying search without content analysis filters...")

                    relevant_docs = self.vector_store.search(
                        query=question,
                        filters=base_filter.build(),
                        k=k,
                    )

                    if not relevant_docs:
                        self.logger.info("Still no relevant documents found without filters.")

            # 7. If still no relevant documents, return a default message
            if not relevant_docs:
                return "I couldn't find any relevant information in the user's content to answer your question."
            else:
                self.logger.info(f"Found {len(relevant_docs)} relevant documents for the query. Docs: {relevant_docs}")

            # 8. Use AI provider to generate answer based on retrieved documents
            context_block = "\n\n".join(relevant_docs)

            answer = self.ai_provider.generate_response(
                context=context_block,
                question=question
            )

            return answer
        except Exception as e:
            self.logger.error(f"Error answering question about profile '{username}': {e}")
            raise e