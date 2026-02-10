from typing import Optional
from pydantic import BaseModel, Field
from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO


class QueryIntentDTO(BaseModel):
    """
    Represents the user's search intent constraints.
    """

    filters: Optional[ContentAnalysisDTO] = Field(
        default=None,
        description="Structured filters to apply based on the user's constraints. Leave fields as None if not specified."
    )