from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING

from .base_repository import BaseRepository
from ..models import ContentAnalysis
from ..models.DTOs.filters.content_analysis_filter import ContentAnalysisFilter
from ..models.utils.taxonomies import *

if TYPE_CHECKING:
    from ..models import Content


class ContentAnalysisRepository(BaseRepository[ContentAnalysis, ContentAnalysisFilter]):
    def __init__(self, session):
        super().__init__(session, ContentAnalysis)


    # *******************************************************
    # Private methods
    # *******************************************************

    def _apply_custom_filters(self, statement: Any, filters: ContentAnalysisFilter) -> Any:
        if filters.season_is:
            statement = self._apply_season_is(statement, filters.season_is)

        if filters.visual_time_of_day_is:
            statement = self._apply_visual_time_of_day_is(statement, filters.visual_time_of_day_is)

        if filters.weather_condition_is:
            statement = self._apply_weather_condition_is(statement, filters.weather_condition_is)

        if filters.location_type_is:
            statement = self._apply_location_type_is(statement, filters.location_type_is)

        if filters.subject_type_is:
            statement = self._apply_subject_type_is(statement, filters.subject_type_is)

        if filters.people_count_is:
            statement = self._apply_people_count_is(statement, filters.people_count_is)

        if filters.main_activity_is:
            statement = self._apply_main_activity_is(statement, filters.main_activity_is)

        if filters.social_context_is:
            statement = self._apply_social_context_is(statement, filters.social_context_is)

        if filters.content_intention_is:
            statement = self._apply_content_intention_is(statement, filters.content_intention_is)

        if filters.mood_is:
            statement = self._apply_mood_is(statement, filters.mood_is)

        if filters.fashion_style_is:
            statement = self._apply_fashion_style_is(statement, filters.fashion_style_is)

        if filters.content_is:
            statement = self._apply_content_is(statement, filters.content_is)

        return statement


    @staticmethod
    def _apply_season_is(statement: Any, value: Season) -> Any:
        return statement.where(ContentAnalysis.season == value)

    @staticmethod
    def _apply_visual_time_of_day_is(statement: Any, value: VisualTimeOfDay) -> Any:
        return statement.where(ContentAnalysis.visual_time_of_day == value)

    @staticmethod
    def _apply_weather_condition_is(statement: Any, value: WeatherCondition) -> Any:
        return statement.where(ContentAnalysis.weather_condition == value)

    @staticmethod
    def _apply_location_type_is(statement: Any, value: LocationType) -> Any:
        return statement.where(ContentAnalysis.location_type == value)

    @staticmethod
    def _apply_subject_type_is(statement: Any, value: SubjectType) -> Any:
        return statement.where(ContentAnalysis.subject_type == value)

    @staticmethod
    def _apply_people_count_is(statement: Any, value: PeopleCount) -> Any:
        return statement.where(ContentAnalysis.people_count == value)

    @staticmethod
    def _apply_main_activity_is(statement: Any, value: MainActivity) -> Any:
        return statement.where(ContentAnalysis.main_activity == value)

    @staticmethod
    def _apply_social_context_is(statement: Any, value: SocialContext) -> Any:
        return statement.where(ContentAnalysis.social_context == value)

    @staticmethod
    def _apply_content_intention_is(statement: Any, value: ContentIntention) -> Any:
        return statement.where(ContentAnalysis.content_intention == value)

    @staticmethod
    def _apply_mood_is(statement: Any, value: Mood) -> Any:
        return statement.where(ContentAnalysis.mood == value)

    @staticmethod
    def _apply_fashion_style_is(statement: Any, value: FashionStyle) -> Any:
        return statement.where(ContentAnalysis.fashion_style == value)

    @staticmethod
    def _apply_content_is(statement: Any, value: Content) -> Any:
        return statement.where(ContentAnalysis.content_id == value.id)