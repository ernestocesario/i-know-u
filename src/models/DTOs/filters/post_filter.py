from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import date

from .base_filter import BaseFilter
from ... import Post, Person


class PostFilter(BaseFilter):
    min_publication_date: Optional[date] = None
    max_publication_date: Optional[date] = None

    caption_contains: Optional[str] = None

    min_n_likes: Optional[int] = None
    max_n_likes: Optional[int] = None

    inference_summary_contains: Optional[str] = None

    owner: Optional[Person] = None