from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel

from .. import ContentAnalysis
from ..utils.taxonomies import *


if TYPE_CHECKING:
    from src.models import ContentAnalysis


class ContentAnalysisDTO(BaseModel):
    # Temporal and environmental attributes
    season: Optional[Season] = None
    visual_time_of_day: Optional[VisualTimeOfDay] = None
    weather_condition: Optional[WeatherCondition] = None
    location_type: Optional[LocationType] = None

    # Subject and activity attributes
    subject_type: Optional[SubjectType] = None
    people_count: Optional[PeopleCount] = None
    main_activity: Optional[MainActivity] = None

    # Social and contextual attributes
    social_context: Optional[SocialContext] = None
    content_intention: Optional[ContentIntention] = None

    # Emotional and stylistic attributes
    mood: Optional[Mood] = None
    fashion_style: Optional[FashionStyle] = None


    def to_entity(self, content_id: int) -> ContentAnalysis:
        """
        Converts this DTO into a SQLModel Entity ready for the database.
        """
        data = self.model_dump(exclude_none=True)

        return ContentAnalysis(
            content_id=content_id,
            **data
        )


    @classmethod
    def from_entity(cls, entity: "ContentAnalysis") -> Optional["ContentAnalysisDTO"]:
        """
        Factory method: Creates a DTO instance from a SQLModel entity.
        Returns None if entity is None.
        """
        if not entity:
            return None

        try:
            return cls(
                season=entity.season,
                visual_time_of_day=entity.visual_time_of_day,
                weather_condition=entity.weather_condition,
                location_type=entity.location_type,
                subject_type=entity.subject_type,
                people_count=entity.people_count,
                main_activity=entity.main_activity,
                social_context=entity.social_context,
                content_intention=entity.content_intention,
                mood=entity.mood,
                fashion_style=entity.fashion_style
            )
        except Exception:
            return None