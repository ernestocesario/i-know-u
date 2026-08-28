import logging
from typing import List, Dict, Any, Optional

from chromadb import Settings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from src.models.DTOs.vector_document_dto import VectorDocumentDTO
from src.models.utils.vector_object_type import VectorObjectType
from src.services.ai.interfaces.base_vector_store import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, google_ai_api_key: str, google_embedding_model: str, persist_directory: str):
        self.logger = logging.getLogger(__name__)

        if not google_ai_api_key:
            raise ValueError("Google AI API Key parameter is missing.")

        if not google_embedding_model:
            raise ValueError("Google Embedding Model parameter is missing.")

        if not persist_directory:
            raise ValueError("Persist Directory parameter is missing.")

        self.persist_directory = persist_directory

        self.embedding_function = GoogleGenerativeAIEmbeddings(
            model=google_embedding_model,
            api_key=SecretStr(google_ai_api_key),
        )

        # Initialize Chroma
        self.vector_store = None
        self.initialize_vector_store()


    def add_document(self, document: VectorDocumentDTO) -> None:
        """
        Embeds and saves textual documents into the vector store.
        """
        if not document.text or not document.text.strip():
            self.logger.warning("Empty document text provided; skipping addition to vector store.")
            return

        try:
            metadata = document.to_chroma_metadata()
            doc = Document(page_content=document.text, metadata=metadata)

            self.vector_store.add_documents([doc])

        except Exception as e:
            self.logger.error(f"Error adding document to vector store: {e}")
            raise e


    def search(self, query: str, filters: Optional[Dict[str, Any]], k: int = 5) -> List[str]:
        """
        Performs a semantic search on the vector store.
        """
        try:
            results = self.vector_store.similarity_search(
                query=query,
                filter=filters,
                k=k,
            )

            return [doc.page_content for doc in results]

        except Exception as e:
            self.logger.error(f"Error during vector search with query '{query}': {e}")
            raise e

    def delete(self, person_id: Optional[int] = None, object_type: Optional[VectorObjectType] = None) -> None:
        """
        Deletes documents from the vector store based on filters.
        Handles the construction of ChromaDB-compliant '$and' clauses.
        """
        try:
            conditions = []

            if person_id is not None:
                conditions.append({"person_id": person_id})

            if object_type:
                conditions.append({"object_type": object_type.value})

            if not conditions:
                self.logger.warning("Delete called without filters. Operation skipped.")
                return

            if len(conditions) == 1:
                where_filter = conditions[0]
            else:
                where_filter = {"$and": conditions}

            self.vector_store.delete(where=where_filter)
            self.logger.info(f"Deleted documents matching: {where_filter}")

        except Exception as e:
            self.logger.error(f"Error deleting from vector store: {e}")
            raise e


    def clear_store(self) -> None:
        """
        Resets the database AND re-initializes the LangChain wrapper.
        """
        try:
            self.logger.info("Resetting Vector Store...")

            # 1. Reset the underlying ChromaDB collection to clear all data
            if not self.vector_store._client.reset():
                raise RuntimeError("Failed to reset the vector store. The collection may be in an inconsistent state.")

            # 2. Re-initialization of the Chroma wrapper to ensure it points to a clean state
            self.initialize_vector_store()

            self.logger.info("Vector store re-initialized successfully.")

        except Exception as e:
            self.logger.error(f"Error resetting vector store: {e}")
            raise e



    # *******************************************************
    # Private methods
    # *******************************************************

    def initialize_vector_store(self) -> None:
        """
        Ensures the vector store is initialized and ready for operations.
        """
        self.vector_store = Chroma(
            collection_name="contents",
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
            client_settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )