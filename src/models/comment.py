from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .post import Post


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)

    publication_date: date = Field()
    text: str = Field()



    # Relationships
    # Many-to-one relationship with Post
    post_id: str = Field(foreign_key="posts.id")
    post: "Post" = Relationship(back_populates="comments")