from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    @abstractmethod
    def analyze_content(self, file_path: str, mime_type: str) -> str:
        """
        Analyzes the content of the given file and returns the inferred text.
        """
        pass


    @abstractmethod
    def generate_response(self, context: str, question: str) -> str:
        """
        Generates a response based on the provided context and question.
        """
        pass