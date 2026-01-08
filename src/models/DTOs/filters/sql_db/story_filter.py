from typing import Optional
from datetime import datetime

from .base_filter import BaseFilter
from src.models import Person


class StoryFilter(BaseFilter):
    min_publication_datetime: Optional[datetime] = None
    max_publication_datetime: Optional[datetime] = None

    processed: Optional[bool] = None


    # Relationship: many-to-one with Person
    owner_is: Optional[Person] = None