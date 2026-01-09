from typing import Optional

from pydantic import BaseModel

from .. import ContentAnalysis
from ..utils.taxonomies import *


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