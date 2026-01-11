import logging
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage
from sqlmodel import Session

from src.repositories.person_repository import PersonRepository
from src.services.ai.interfaces.base_ai_provider import BaseAIProvider
from src.services.ai.prompts.report_prompts import ReportTemplates
from src.services.profile_query_service import ProfileQueryService
from src.services.storage.file_storage_manager import FileStorageManager


class ReportService:
    def __init__(
            self,
            session: Session,
            profile_query_service: ProfileQueryService,
            ai_provider: BaseAIProvider,
            file_manager: FileStorageManager
    ):
        self.logger = logging.getLogger(__name__)

        self.session = session
        self.profile_query_service = profile_query_service
        self.ai_provider = ai_provider
        self.file_manager = file_manager

        self.person_repository = PersonRepository(session)


    def generate_report(self, username: str) -> str:
        """
        Orchestrates the generation of a full profile report.
        1. Fetches User Metadata.
        2. Iterates through specific research questions via RAG.
        3. Compiles everything into a Markdown report via LLM.
        4. Saves to Disk.
        """
        person = self.person_repository.get_by_username(username)
        if not person:
            raise ValueError(f"User {username} not found.")

        self.logger.info(f"Starting report generation for @{username}...")

        # 1. Collect Research Data (The Map Phase)
        research_notes = []

        for section_title, question in ReportTemplates.REPORT_SECTIONS_QUESTIONS:
            try:
                # Use the existing RAG service to get a factual answer based on vectors
                # We use a lower 'k' (e.g., 10) to be precise for each section
                answer = self.profile_query_service.ask_question_about_profile(
                    username=username,
                    question=question,
                    k=20
                )
                research_notes.append(f"### FINDINGS FOR '{section_title}':\n{answer}\n")
            except Exception as e:
                self.logger.warning(f"Failed to analyze section '{section_title}': {e}")
                research_notes.append(f"### FINDINGS FOR '{section_title}':\n[Data missing due to error]\n")

        # 2. Compile the Report (The Reduce Phase)
        full_research_text = "\n".join(research_notes)

        # Prepare context for the compiler
        compiler_system_prompt = ReportTemplates.REPORT_COMPILER_SYSTEM.format(
            username=person.username,
            date=datetime.now().strftime("%Y-%m-%d"),
            full_name=person.full_name or "Unknown",
            followers=person.n_followers or 0
        )

        compiler_user_prompt = ReportTemplates.REPORT_COMPILER_USER.format(
            research_data=full_research_text
        )

        try:
            # Direct call to LLM (bypassing RAG because we already have the context)
            messages = [
                SystemMessage(content=compiler_system_prompt),
                HumanMessage(content=compiler_user_prompt)
            ]

            final_markdown = self.ai_provider.generate_raw(messages)

            # 3. Save
            saved_path = self.file_manager.save_report(
                user_external_id=person.external_id,
                username=person.username,
                markdown_content=final_markdown
            )

            return saved_path

        except Exception as e:
            self.logger.error(f"Failed to compile report: {e}")
            raise e