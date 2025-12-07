from __future__ import annotations

from datetime import date
from typing import Optional

from .base_filter import BaseFilter
from ... import Person


class PostFilter(BaseFilter):
    min_publication_date: Optional[date] = None
    max_publication_date: Optional[date] = None

    caption_contains: Optional[str] = None

    min_n_likes: Optional[int] = None
    max_n_likes: Optional[int] = None

    inference_summary_contains: Optional[str] = None

    owner_is: Optional[Person] = None