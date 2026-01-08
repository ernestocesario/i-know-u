from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.utils.vector_metadata_keys import VectorMetadataKeys
from src.models.utils.vector_object_type import VectorObjectType


class VectorFilter(BaseModel):
    person_id: Optional[int] = None
    object_type: Optional[VectorObjectType] = None
    object_id: Optional[int] = None
    mime_type: Optional[str] = None

    ContentAnalysisDTO: Optional[ContentAnalysisDTO] = None


    def build_filter(self) -> Optional[Dict[str, Any]]:
        """
        Translates the filter object into ChromaDB specific query syntax.
        Directly builds the dictionary for implicit AND logic.
        """
        vector_filter: Dict[str, Any] = {}

        # 1. Map Structural Filters using CONSTANTS
        if self.person_id is not None:
            vector_filter[VectorMetadataKeys.PERSON_ID] = self.person_id

        if self.object_type is not None:
            vector_filter[VectorMetadataKeys.OBJECT_TYPE] = self.object_type.value

        if self.object_id is not None:
            vector_filter[VectorMetadataKeys.OBJECT_ID] = self.object_id

        if self.mime_type is not None:
            vector_filter[VectorMetadataKeys.MIME_TYPE] = self.mime_type

        # 2. Map Analysis Filters (Dynamic unpacking)
        if self.content_analysis:
            analysis_dict = self.content_analysis.model_dump(exclude_none=True)

            for key, value in analysis_dict.items():
                vector_filter[key] = str(value)

        # Return None if dictionary is empty (no filter applied)
        return vector_filter if vector_filter else None