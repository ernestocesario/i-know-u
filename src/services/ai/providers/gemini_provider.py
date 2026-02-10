import logging
import os
import time
from typing import List, Optional

from google import genai
from google.genai import types
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.DTOs.query_intent_dto import QueryIntentDTO
from src.services.ai.interfaces.base_ai_provider import BaseAIProvider
from src.services.ai.prompts.prompts import PromptTemplates


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
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

        self.content_analysis_llm = self.llm.with_structured_output(ContentAnalysisDTO)
        self.query_intent_llm = self.llm.with_structured_output(QueryIntentDTO)


    # *******************************************************
    # Public methods
    # *******************************************************

    def get_content_description(self, file_path: str, mime_type: str, caption: Optional[str] = None) -> str:
        """
        Analyzes the content of the given file and returns the inferred text.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        google_file = None

        try:
            google_file = self._upload_file_to_google(file_path, mime_type)

            # 1. Prepare Instructions
            text_instruction = PromptTemplates.MEDIA_ANALYSIS_INSTRUCTION

            # 2. Inject Caption if exists
            if caption:
                text_instruction += PromptTemplates.CAPTION_CONTEXT_INSTRUCTION.format(caption=caption)

            messages: List[BaseMessage] = [
                SystemMessage(content=PromptTemplates.VISUAL_ANALYSIS_SYSTEM),
                HumanMessage(
                    content=[
                        {"type": "text", "text": text_instruction},
                        {"type": "media", "file_uri": google_file.uri, "mime_type": mime_type}
                    ]
                )
            ]

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


    def get_content_analysis(self, file_path: str, mime_type: str, caption: Optional[str] = None) -> ContentAnalysisDTO:
        """
        Analyzes the content of the given file and returns structured metadata (Mood, Season, etc.).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        google_file = None
        try:
            google_file = self._upload_file_to_google(file_path, mime_type)

            # 1. Prepare Instructions
            text_instruction = PromptTemplates.STRUCTURED_ANALYSIS_INSTRUCTION
            if caption:
                text_instruction += PromptTemplates.CAPTION_CONTEXT_INSTRUCTION.format(caption=caption)

            messages: List[BaseMessage] = [
                HumanMessage(
                    content=[
                        {"type": "text", "text": text_instruction},
                        {"type": "media", "file_uri": google_file.uri, "mime_type": mime_type}
                    ]
                )
            ]

            content_analysis_dto = self.content_analysis_llm.invoke(messages)
            return content_analysis_dto
        except Exception as e:
            self.logger.error(f"Error getting structured analysis from file '{file_path}': {e}")
            raise e
        finally:
            if google_file:
                try:
                    self._delete_file_from_google(google_file)
                except Exception as cleanup_error:
                    self.logger.warning(f"Error deleting Google file '{google_file.name}': {cleanup_error}")


    def extract_search_intent(self, question: str) -> QueryIntentDTO:
        formatted_instruction = PromptTemplates.SEARCH_QUERY_OPTIMIZER_USER_QUESTION.format(
            question=question
        )

        messages = [
            SystemMessage(content=PromptTemplates.SEARCH_QUERY_OPTIMIZER_SYSTEM),
            HumanMessage(content=formatted_instruction)
        ]

        try:
            return self.query_intent_llm.invoke(messages)
        except Exception as e:
            self.logger.error(f"Error extracting search intent from question '{question}': {e}")

            return QueryIntentDTO(filters=None)


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


    def summarize_collection(self, descriptions: List[str], caption: Optional[str] = None) -> str:
        """
        Aggregates multiple contents descriptions into a summary for (Post/Highlight).
        """
        if not descriptions:
            return ""

        try:
            bullet_points = "\n".join([f"- {desc}" for desc in descriptions])

            # Prepare optional caption text
            caption_text = ""
            if caption:
                caption_text = f"USER ORIGINAL CAPTION:\n'{caption}'\n"

            formatted_instruction = PromptTemplates.SUMMARIZATION_INSTRUCTION.format(
                items_descriptions=bullet_points,
                caption_context=caption_text
            )

            messages = [
                SystemMessage(content=PromptTemplates.PARENT_SUMMARIZATION_SYSTEM),
                HumanMessage(content=formatted_instruction)
            ]

            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            raise e


    def enrich_profile(self, username: str, full_name: str, bio: str, stats: dict) -> str:
        try:
            formatted_instruction = PromptTemplates.PROFILE_ENRICHMENT_USER.format(
                username=username,
                full_name=full_name or "Not provided",
                bio=bio or "Empty bio",
                n_followers=stats.get("followers", 0),
                n_following=stats.get("following", 0),
                n_posts=stats.get("posts", 0)
            )

            messages: List[BaseMessage] = [
                SystemMessage(content=PromptTemplates.PROFILE_ENRICHMENT_SYSTEM),
                HumanMessage(content=formatted_instruction)
            ]

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            self.logger.error(f"Profile enrichment failed for {username}: {e}")
            raise e


    def generate_raw(self, messages: List[BaseMessage]) -> str:
        """
        Direct invocation of the LLM.
        """
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            self.logger.error(f"Error in generate_raw: {e}")
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

        while google_file.state == types.FileState.PROCESSING:
            time.sleep(1)
            google_file = self.client.files.get(name=google_file.name)

        if google_file.state.name != types.FileState.ACTIVE:
            raise ValueError(f"Google file upload failed: {google_file.error.message}")

        return google_file


    def _delete_file_from_google(self, google_file: types.File):
        """
        Helper method to delete a file from Google's cloud storage.
        """

        self.client.files.delete(name=google_file.name)