from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

from src.models.utils.taxonomies import *

if TYPE_CHECKING:
    from .content import Content


class ContentAnalysis(SQLModel, table=True):
    __tablename__ = "content_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Temporal and environmental attributes
    season: Season = Field(index=True)
    visual_time_of_day: VisualTimeOfDay = Field(index=True)
    weather_condition: WeatherCondition = Field(index=True)
    location_type: LocationType = Field(index=True)

    # Subject and activity attributes
    subject_type: SubjectType = Field(index=True)
    people_count: PeopleCount = Field(index=True)
    main_activity: MainActivity = Field(index=True)

    # Social and contextual attributes
    social_context: SocialContext = Field(index=True)
    content_intention: ContentIntention = Field(index=True)

    # Emotional and stylistic attributes
    mood: Mood = Field(index=True)
    fashion_style: FashionStyle = Field(index=True)



    # Relationships
    # One-to-one relationship with Content
    content_id: int = Field(foreign_key="contents.id", unique=True)
    content: Content = Relationship(back_populates="content_analysis")