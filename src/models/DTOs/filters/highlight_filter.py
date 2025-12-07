from typing import Optional

from .base_filter import BaseFilter
from ... import Person


class HighlightFilter(BaseFilter):
    title_contains: Optional[str] = None

    inference_summary_contains: Optional[str] = None


    # Relationship: many-to-one with Person
    owner_is: Optional[Person] = None