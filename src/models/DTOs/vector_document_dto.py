from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.utils.VectorObjectType import VectorObjectType


class VectorDocumentDTO(BaseModel):
    text: str
    person_id: int
    object_id: int

    object_type: VectorObjectType
    mime_type: Optional[str] = None

    content_analysis: Optional[ContentAnalysisDTO] = None


    def to_chroma_metadata(self) -> Dict[str, Any]:
        """
        Converts the typed DTOs into a flat dictionary of primitives
        compatible with ChromaDB.
        """

        # 1. Base metadata
        metadata = {
            "person_id": self.person_id,
            "object_id": self.object_id,
            "object_type": self.object_type.value,
        }

        # 2. Add mime_type if present
        if self.mime_type:
            metadata["mime_type"] = self.mime_type

        # 3. Flatten content analysis if present
        if self.content_analysis:
            content_analysis_dict = self.content_analysis.model_dump(exclude_none=True)

            for key, value in content_analysis_dict.items():
                metadata[key] = str(value)

        return metadata