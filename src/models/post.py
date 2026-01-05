from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .person import Person
    from .content import Content
    from .comment import Comment

class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)

    publication_datetime: Optional[datetime] = Field(default=None)
    caption: Optional[str] = Field(default=None)
    n_likes: Optional[int] = Field(default=None)

    # calculated by AI models
    inference_summary: Optional[str] = Field(default=None)



    # Relationships
    # Many-to-one relationship with Person
    owner_id: int = Field(foreign_key="persons.id")
    owner: Person = Relationship(back_populates="posts")

    # One-to-many relationship with Content
    contents: list[Content] = Relationship(back_populates="post")

    # One-to-many relationship with Comment
    comments: list[Comment] = Relationship(back_populates="post")
