from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .post import Post
    from .highlight import Highlight
    from .story import Story
    from .content_analysis import ContentAnalysis


class Content(SQLModel, table=True):
    __tablename__ = "contents"

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)

    publication_datetime: Optional[datetime] = Field(default=None)

    mime_type: str = Field()

    # calculated by AI models
    inferred_text: Optional[str] = Field(default=None)

    processed: bool = Field(default=False)



    # Relationships
    # Many-to-one relationship with Post
    post_id: Optional[int] = Field(foreign_key="posts.id")
    post: Optional[Post] = Relationship(back_populates="contents")

    # Many-to-one relationship with Highlight
    highlight_id: Optional[int] = Field(foreign_key="highlights.id")
    highlight: Optional[Highlight] = Relationship(back_populates="contents")

    # Many-to-one relationship with Story
    story_id: Optional[int] = Field(foreign_key="stories.id")
    story: Optional[Story] = Relationship(back_populates="contents")

    # One-to-one relationship with ContentAnalysis
    content_analysis: Optional[ContentAnalysis] = Relationship(
        back_populates="content",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
