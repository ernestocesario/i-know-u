from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .person import Person
    from .content import Content
    from .comment import Comment

class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: str = Field(primary_key=True, index=True)
    publication_date: date = Field()
    caption: Optional[str] = Field(default=None)
    n_likes: int = Field(default=0)

    # calculated by AI models
    inference_summary: Optional[str] = Field(default=None)



    # Relationships
    # Many-to-one relationship with Person
    owner_id: str = Field(foreign_key="persons.id")
    owner: Person = Relationship(back_populates="posts")

    # One-to-many relationship with Content
    contents: list[Content] = Relationship(back_populates="post")

    # One-to-many relationship with Comment
    comments: list[Comment] = Relationship(back_populates="post")
