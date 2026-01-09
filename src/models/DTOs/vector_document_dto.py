from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.utils.vector_object_type import VectorObjectType
from src.models.utils.vector_metadata_keys import VectorMetadataKeys


class VectorDocumentDTO(BaseModel):
    text: str
    person_id: int
    object_id: int

    object_type: VectorObjectType
    mime_type: Optional[str] = None

    content_analysis_dto: Optional[ContentAnalysisDTO] = None


    def to_chroma_metadata(self) -> Dict[str, Any]:
        """
        Converts the typed DTOs into a flat dictionary of primitives
        compatible with ChromaDB.
        """

        # 1. Base metadata
        metadata = {
            VectorMetadataKeys.PERSON_ID: self.person_id,
            VectorMetadataKeys.OBJECT_ID: self.object_id,
            VectorMetadataKeys.OBJECT_TYPE: self.object_type.value,
        }

        # 2. Add mime_type if present
        if self.mime_type:
            metadata[VectorMetadataKeys.MIME_TYPE] = self.mime_type

        # 3. Flatten content analysis if present
        if self.content_analysis_dto:
            content_analysis_dict = self.content_analysis_dto.model_dump(exclude_none=True)

            for key, value in content_analysis_dict.items():
                metadata[key] = str(value)

        return metadata