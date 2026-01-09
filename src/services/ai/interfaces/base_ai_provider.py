from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO


class BaseAIProvider(ABC):

    @abstractmethod
    def get_content_description(self, file_path: str, mime_type: str) -> str:
        """
        Analyzes the content of the given file and returns the inferred text.
        """
        pass


    @abstractmethod
    def get_content_analysis(self, file_path: str, mime_type: str) -> ContentAnalysisDTO:
        """
        Analyzes the image/video and returns structured metadata (Mood, Season, etc.).
        Returns a DTO, not a DB Entity.
        """
        pass


    @abstractmethod
    def generate_response(self, context: str, question: str) -> str:
        """
        Generates a response based on the provided context and question (RAG).
        """
        pass


    @abstractmethod
    def summarize_collection(self, descriptions: List[str]) -> str:
        """
        Aggregates multiple contents descriptions into a summary for (Post/Highlight).
        """
        pass