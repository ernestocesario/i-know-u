from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseVectorStore(ABC):
    """
    Abstract Base Class defining the contract for Vector Database interactions.
    """

    @abstractmethod
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Embeds and saves textual documents into the vector store.

        Args:
            texts: List of strings (descriptions) to embed.
            metadatas: List of dictionaries containing metadata (e.g., {'owner_id': '123'}).
        """
        pass

    @abstractmethod
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None, k: int = 5) -> List[str]:
        """
        Performs a semantic search on the vector store.

        Args:
            query: The user's question.
            filters: Optional filters (e.g., search only specific user).
            k: Number of results to return.

        Returns:
            List[str]: List of relevant text snippets (context).
        """
        pass

    @abstractmethod
    def delete_collection(self, owner_id: str) -> None:
        """
        Removes vectors associated with a specific owner.
        """
        pass