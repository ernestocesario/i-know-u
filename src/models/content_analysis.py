from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from src.models.utils.taxonomies import *

if TYPE_CHECKING:
    from .content import Content


class ContentAnalysis(SQLModel, table=True):
    __tablename__ = "content_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Temporal and environmental attributes
    season: Season = Field(default=Season.UNDEFINED, index=True)
    visual_time_of_day: VisualTimeOfDay = Field(default=VisualTimeOfDay.UNDEFINED, index=True)
    weather_condition: WeatherCondition = Field(default=WeatherCondition.UNDEFINED, index=True)
    location_type: LocationType = Field(default=LocationType.UNDEFINED, index=True)

    # Subject and activity attributes
    subject_type: SubjectType = Field(default=SubjectType.UNDEFINED, index=True)
    people_count: PeopleCount = Field(default=PeopleCount.UNDEFINED, index=True)
    main_activity: MainActivity = Field(default=MainActivity.UNDEFINED, index=True)

    # Social and contextual attributes
    social_context: SocialContext = Field(default=SocialContext.UNDEFINED, index=True)
    content_intention: ContentIntention = Field(default=ContentIntention.UNDEFINED, index=True)

    # Emotional and stylistic attributes
    mood: Mood = Field(default=Mood.UNDEFINED, index=True)
    fashion_style: FashionStyle = Field(default=FashionStyle.UNDEFINED, index=True)



    # Relationships
    # One-to-one relationship with Content
    content_id: int = Field(foreign_key="contents.id", unique=True)
    content: "Content" = Relationship(back_populates="content_analysis")