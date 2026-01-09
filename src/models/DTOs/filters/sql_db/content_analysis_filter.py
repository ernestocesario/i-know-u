from typing import Optional

from src.models import Content
from src.models.utils.taxonomies import *
from .base_filter import BaseFilter


class ContentAnalysisFilter(BaseFilter):

    #  Temporal and environmental attributes
    season_is: Optional[Season] = None
    visual_time_of_day_is: Optional[VisualTimeOfDay] = None
    weather_condition_is: Optional[WeatherCondition] = None
    location_type_is: Optional[LocationType] = None

    # Subject and activity attributes
    subject_type_is: Optional[SubjectType] = None
    people_count_is: Optional[PeopleCount] = None
    main_activity_is: Optional[MainActivity] = None

    # Social and contextual attributes
    social_context_is: Optional[SocialContext] = None
    content_intention_is: Optional[ContentIntention] = None

    # Emotional and stylistic attributes
    mood_is: Optional[Mood] = None
    fashion_style_is: Optional[FashionStyle] = None


    # Relationship: one-to-one with Content
    content_is: Optional[Content] = None