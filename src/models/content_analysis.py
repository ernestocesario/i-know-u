from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from src.models.utils.taxonomies import *

if TYPE_CHECKING:
    from .content import Content


class ContentAnalysis(SQLModel, table=True):
    __tablename__ = "content_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Temporal and environmental attributes
    season: Optional[Season] = Field(default=None, nullable=True, index=True)
    visual_time_of_day: Optional[VisualTimeOfDay] = Field(default=None, nullable=True, index=True)
    weather_condition: Optional[WeatherCondition] = Field(default=None, nullable=True, index=True)
    location_type: Optional[LocationType] = Field(default=None, nullable=True, index=True)

    # Subject and activity attributes
    subject_type: Optional[SubjectType] = Field(default=None, nullable=True, index=True)
    people_count: Optional[PeopleCount] = Field(default=None, nullable=True, index=True)
    main_activity: Optional[MainActivity] = Field(default=None, nullable=True, index=True)

    # Social and contextual attributes
    social_context: Optional[SocialContext] = Field(default=None, nullable=True, index=True)
    content_intention: Optional[ContentIntention] = Field(default=None, nullable=True, index=True)

    # Emotional and stylistic attributes
    mood: Optional[Mood] = Field(default=None, nullable=True, index=True)
    fashion_style: Optional[FashionStyle] = Field(default=None, nullable=True, index=True)



    # Relationships
    # One-to-one relationship with Content
    content_id: int = Field(foreign_key="contents.id", unique=True)
    content: "Content" = Relationship(back_populates="content_analysis")