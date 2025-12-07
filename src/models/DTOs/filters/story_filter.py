from typing import Optional
from datetime import date

from .base_filter import BaseFilter
from ... import Person


class StoryFilter(BaseFilter):
    min_publication_date: Optional[date] = None
    max_publication_date: Optional[date] = None

    processed: Optional[bool] = None

    owner: Optional[Person] = None