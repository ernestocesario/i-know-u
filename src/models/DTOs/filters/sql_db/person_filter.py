from typing import Optional

from .base_filter import BaseFilter


class PersonFilter(BaseFilter):
    username_contains: Optional[str] = None
    full_name_contains: Optional[str] = None
    bio_contains: Optional[str] = None

    min_n_followers: Optional[int] = None
    max_n_followers: Optional[int] = None

    min_n_following: Optional[int] = None
    max_n_following: Optional[int] = None

    min_n_posts: Optional[int] = None
    max_n_posts: Optional[int] = None

    inferred_text_contains: Optional[str] = None

    processed_is: Optional[bool] = None