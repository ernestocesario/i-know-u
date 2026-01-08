from typing import Optional
from datetime import datetime

from .base_filter import BaseFilter
from src.models import Post, Highlight, Story, ContentAnalysis


class ContentFilter(BaseFilter):
    min_publication_datetime: Optional[datetime] = None
    max_publication_datetime: Optional[datetime] = None

    inferred_text_contains: Optional[str] = None

    processed_is: Optional[bool] = None


    # Relationship: many-to-one with Post
    post_is: Optional[Post] = None

    # Relationship: many-to-one with Highlight
    highlight_is: Optional[Highlight] = None

    # Relationship: many-to-one with Story
    story_is: Optional[Story] = None

    # Relationship: one-to-one with ContentAnalysis
    content_analysis_is: Optional[ContentAnalysis] = None