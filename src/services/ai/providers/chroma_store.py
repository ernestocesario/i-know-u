import logging
from typing import List, Dict, Any, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from src.config.app_properties import AppProperties
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


    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Embeds and saves textual documents into the vector store.
        """
        if not texts:
            self.logger.warning("No texts provided to add to the vector store.")
            return

        try:
            documents = [
                Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas)
            ]

            self.vector_store.add_documents(documents)

        except Exception as e:
            self.logger.error(f"Error adding documents to vector store: {e}")
            raise e


    def search(self, query: str, filters: Optional[Dict[str, Any]] = None, k: int = 5) -> List[str]:
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
            self.logger.error(f"Error searching vector store: {e}")
            raise e


    def delete_contents(self, owner_id: str):
        """
        Removes vectors associated with a specific owner.
        """
        try:
            self.vector_store.delete(where={"owner_id": owner_id})

        except Exception as e:
            self.logger.error(f"Error deleting contents for owner_id '{owner_id}': {e}")
            raise e