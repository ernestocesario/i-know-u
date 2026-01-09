from typing import Optional
from datetime import datetime

from .base_filter import BaseFilter
from src.models import Person


class PostFilter(BaseFilter):
    min_publication_datetime: Optional[datetime] = None
    max_publication_datetime: Optional[datetime] = None

    caption_contains: Optional[str] = None

    min_n_likes: Optional[int] = None
    max_n_likes: Optional[int] = None

    processed_is: Optional[bool] = None

    inference_summary_contains: Optional[str] = None


    # Relationship: many-to-one with Person
    owner_is: Optional[Person] = None