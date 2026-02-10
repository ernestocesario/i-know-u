from abc import ABC, abstractmethod
from typing import List, Optional

from langchain_core.messages import BaseMessage

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.DTOs.query_intent_dto import QueryIntentDTO


class BaseAIProvider(ABC):

    @abstractmethod
    def get_content_description(self, file_path: str, mime_type: str, caption: Optional[str] = None) -> str:
        """
        Analyzes the content of the given file and returns the inferred text.
        """
        pass


    @abstractmethod
    def get_content_analysis(self, file_path: str, mime_type: str, caption: Optional[str] = None) -> ContentAnalysisDTO:
        """
        Analyzes the image/video and returns structured metadata (Mood, Season, etc.).
        Returns a DTO, not a DB Entity.
        """
        pass


    @abstractmethod
    def extract_search_intent(self, question: str) -> QueryIntentDTO:
        """
        Analyzes the user's natural language question and extracts:
        1. A cleaner semantic search query.
        2. Structured filters (Season, Mood, etc.) to apply to the vector DB.
        """
        pass


    @abstractmethod
    def generate_response(self, context: str, question: str) -> str:
        """
        Generates a response based on the provided context and question (RAG).
        """
        pass


    @abstractmethod
    def summarize_collection(self, descriptions: List[str], caption: Optional[str] = None) -> str:
        """
        Aggregates multiple contents descriptions into a summary for (Post/Highlight).
        """
        pass


    @abstractmethod
    def enrich_profile(self, username: str, full_name: str, bio: str, stats: dict) -> str:
        """
        Generates a narrative profile description based on raw metadata.
        """
        pass


    @abstractmethod
    def generate_raw(self, messages: List[BaseMessage]) -> str:
        """
        Directly invokes the LLM with a list of messages.
        Useful for custom tasks like report compilation.
        """
        pass