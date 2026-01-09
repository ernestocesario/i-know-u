from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .post import Post
    from .highlight import Highlight
    from .story import Story

class Person(SQLModel, table=True):
    __tablename__ = "persons"

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)

    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = Field(index=True)
    bio: Optional[str] = Field(default=None)
    n_followers: Optional[int] = Field(default=None)
    n_following: Optional[int] = Field(default=None)
    n_posts: Optional[int] = Field(default=None)

    # calculated by AI models
    inferred_text: Optional[str] = Field(default=None)

    processed: bool = Field(default=False)



    # Relationships
    # One-to-many relationship with Post
    posts: List[Post] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # One-to-many relationship with Highlight
    highlights: List[Highlight] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # One-to-many relationship with Story
    stories: List[Story] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
