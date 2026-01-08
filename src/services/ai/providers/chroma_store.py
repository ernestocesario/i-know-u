import logging
from typing import List, Dict, Any, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from src.config.app_properties import AppProperties
from src.models.DTOs.filters.vector_db.vector_filter import VectorFilter
from src.models.DTOs.vector_document_dto import VectorDocumentDTO
from src.models.utils.vector_object_type import VectorObjectType
from src.models.utils.vector_metadata_keys import VectorMetadataKeys
from src.services.ai.interfaces.base_vector_store import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)

        if not api_key:
            raise ValueError("Google API Key is missing. Please set GOOGLE_API_KEY environment variable.")

        self.embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            api_key=SecretStr(api_key),
        )

        self.persist_directory = AppProperties.VECTOR_STORE_DIR

        # Initialize Chroma
        self.vector_store = Chroma(
            collection_name="contents",
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
        )


    def add_documents(self, document: VectorDocumentDTO) -> None:
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


    def search(self, query: str, filters: Optional[VectorFilter], k: int = 5) -> List[str]:
        """
        Performs a semantic search on the vector store.
        """
        try:
            results = self.vector_store.similarity_search(
                query=query,
                filters=filters.build_filter(),
                k=k,
            )

            return [doc.page_content for doc in results]

        except Exception as e:
            self.logger.error(f"Error during vector search with query '{query}': {e}")
            raise e


    def delete(self, person_id: int, object_type: Optional[VectorObjectType] = None) -> None:
        try:
            where_filter: Dict[str, Any] = {VectorMetadataKeys.PERSON_ID: person_id}

            if object_type:
                where_filter[VectorMetadataKeys.OBJECT_TYPE] = object_type.value

            self.vector_store.delete(where=where_filter)

        except Exception as e:
            self.logger.error(f"Error deleting vectors for {VectorMetadataKeys.PERSON_ID} '{person_id}' and {VectorMetadataKeys.OBJECT_TYPE} '{object_type}': {e}")
            raise e


    def clear_store(self) -> None:
        """
        Clears the entire vector store.
        """
        try:
            self.vector_store.delete(where={})
        except Exception as e:
            self.logger.error(f"Error clearing the vector store: {e}")
            raise e