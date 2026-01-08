from typing import Optional
from datetime import datetime

from .base_filter import BaseFilter
from src.models import Post


class CommentFilter(BaseFilter):
    min_publication_datetime: Optional[datetime] = None
    max_publication_datetime: Optional[datetime] = None

    text_contains: Optional[str] = None


    # Relationship: many-to-one with Post
    post_is: Optional[Post] = None