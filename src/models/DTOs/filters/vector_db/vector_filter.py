from __future__ import annotations
from typing import Optional, Dict, Any, List, Literal, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel

from src.models.DTOs.content_analysis_dto import ContentAnalysisDTO
from src.models.utils.vector_metadata_keys import VectorMetadataKeys
from src.models.utils.vector_object_type import VectorObjectType

# Define the specific types allowed in the query tree for Pydantic validation
VectorQueryNodeType = Union['VectorFilter', 'VectorQueryCombination']


class VectorQueryNode(ABC):
    """
    Abstract Base Class acting as an interface for query nodes.
    Implements logical operators (&, |) for easy query construction.
    """

    @abstractmethod
    def build(self) -> Optional[Dict[str, Any]]:
        """Generates the ChromaDB compatible dictionary."""
        pass

    def __or__(self, other: Optional[VectorQueryNodeType]) -> VectorQueryNodeType:
        if not other:
            return self
        return VectorQueryCombination(operator="$or", operands=[self, other])

    def __and__(self, other: Optional[VectorQueryNodeType]) -> VectorQueryNodeType:
        if not other:
            return self
        return VectorQueryCombination(operator="$and", operands=[self, other])


class VectorQueryCombination(BaseModel, VectorQueryNode):
    """
    Composite Node: Represents a logical combination (AND/OR) of other nodes.
    """
    operator: Literal["$and", "$or"]
    operands: List[VectorQueryNodeType]

    def build(self) -> Optional[Dict[str, Any]]:
        # Recursively build child conditions
        conditions = [op.build() for op in self.operands if op]

        # Filter out None results
        valid_conditions = [c for c in conditions if c is not None]

        if not valid_conditions:
            return None

        # Optimization: unwraps single conditions
        if len(valid_conditions) == 1:
            return valid_conditions[0]

        return {self.operator: valid_conditions}


class VectorFilter(BaseModel, VectorQueryNode):
    """
    Leaf Node: Represents a specific set of filtering criteria.
    """
    person_id: Optional[int] = None
    object_type: Optional[VectorObjectType] = None
    object_id: Optional[int] = None
    mime_type: Optional[str] = None
    content_analysis_dto: Optional[ContentAnalysisDTO] = None

    def build(self) -> Optional[Dict[str, Any]]:
        """
        Translates specific attributes into a ChromaDB query dict.
        """
        conditions: List[Dict[str, Any]] = []

        # 1. Base Metadata
        if self.person_id is not None:
            conditions.append({VectorMetadataKeys.PERSON_ID: self.person_id})
        if self.object_type is not None:
            conditions.append({VectorMetadataKeys.OBJECT_TYPE: self.object_type.value})
        if self.object_id is not None:
            conditions.append({VectorMetadataKeys.OBJECT_ID: self.object_id})
        if self.mime_type is not None:
            conditions.append({VectorMetadataKeys.MIME_TYPE: self.mime_type})

        # 2. Content Analysis Metadata
        if self.content_analysis_dto:
            analysis_dict = self.content_analysis_dto.model_dump(exclude_none=True)
            for key, value in analysis_dict.items():
                # Safe extraction of Enum values
                clean_value = getattr(value, "value", value)
                conditions.append({key: clean_value})

        if not conditions:
            return None

        # Return single condition directly or wrapped in implicit AND
        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}