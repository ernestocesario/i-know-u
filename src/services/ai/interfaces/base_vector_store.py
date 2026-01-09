from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.DTOs.filters.vector_db.vector_filter import VectorFilter
from src.models.DTOs.vector_document_dto import VectorDocumentDTO
from src.models.utils.vector_object_type import VectorObjectType


class BaseVectorStore(ABC):
    """
    Abstract Base Class defining the contract for Vector Database interactions.
    """

    @abstractmethod
    def add_document(self, document: VectorDocumentDTO) -> None:
        """
        Embeds and saves textual documents into the vector store.
        """
        pass


    @abstractmethod
    def search(self, query: str, filters: Optional[VectorFilter], k: int = 5) -> List[str]:
        """
        Performs a semantic search on the vector store.
        """
        pass


    @abstractmethod
    def delete(self, person_id: int, object_type: Optional[VectorObjectType] = None) -> None:
        """
        Removes all vectors of a specific type associated with a specific person.
        If object_type is None, removes all vectors for the person.
        """
        pass


    @abstractmethod
    def clear_store(self) -> None:
        """
        Clears the entire vector store.
        """
        pass