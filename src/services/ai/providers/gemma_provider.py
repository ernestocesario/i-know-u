import logging
import os
from typing import List

from google import genai
from google.genai import types
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.services.ai.interfaces.base_ai_provider import BaseAIProvider
from src.services.ai.prompts import PromptTemplates


class GemmaProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemma-3-27b-it"):
        self.logger = logging.getLogger(__name__)

        if not api_key:
            raise ValueError("Google API Key is missing. Please set GOOGLE_API_KEY environment variable.")

        # Native SDK configuration (required for File API uploads)
        self.client = genai.Client(api_key=api_key)

        # Langchain configuration
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0
        )


    # *******************************************************
    # Public methods
    # *******************************************************

    def analyze_content(self, file_path: str, mime_type: str) -> str:
        """
        Analyzes the content of the given file and returns the inferred text.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        google_file = None

        try:
            # Upload file to Google Cloud Storage
            google_file = self._upload_file_to_google(file_path, mime_type)

            # Build the prompt to analyze the file
            messages: List[BaseMessage] = [
                SystemMessage(content=PromptTemplates.VISUAL_ANALYSIS_SYSTEM),
                HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": PromptTemplates.MEDIA_ANALYSIS_INSTRUCTION
                        },
                        {
                            "type": "media",
                            "file_uri": google_file.uri,
                            "mime_type": mime_type
                        }
                    ]
                )
            ]

            # Invoke the model
            response = self.llm.invoke(messages)

            return response.content

        except Exception as e:
            self.logger.error(f"Error analyzing content from file '{file_path}': {e}")
            raise e

        finally:
            # Clean up: delete the uploaded file from Google Cloud Storage
            if google_file:
                try:
                    self._delete_file_from_google(google_file)
                except Exception as cleanup_error:
                    self.logger.warning(f"Error deleting Google file '{google_file.name}': {cleanup_error}")


    def generate_response(self, context: str, question: str) -> str:
        """
        Generates a response based on the provided context and question.
        """

        try:
            formatted_text = PromptTemplates.RAG_QA_SYSTEM.format(
                context=context,
                question=question
            )

            messages: List[BaseMessage] = [
                HumanMessage(content=formatted_text)
            ]

            response = self.llm.invoke(messages)

            return response.content

        except Exception as e:
            self.logger.error(f"Error generating response for question '{question}': {e}")
            raise e



    # *******************************************************
    # Private methods
    # *******************************************************

    def _upload_file_to_google(self, file_path: str, mime_type: str) -> types.File:
        """
        Helper method to upload a file to Google's cloud storage.
        Necessary because Google AI models requires a file URI for file input.
        """

        google_file = self.client.files.upload(file=file_path, config=types.UploadFileConfig(mime_type=mime_type))

        if google_file.state.name != types.FileState.ACTIVE:
            raise ValueError(f"Google file upload failed: {google_file.error.message}")

        return google_file


    def _delete_file_from_google(self, google_file: types.File):
        """
        Helper method to delete a file from Google's cloud storage.
        """

        self.client.files.delete(name=google_file.name)