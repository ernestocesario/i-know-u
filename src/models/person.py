from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .post import Post
    from .highlight import Highlight
    from .story import Story

class Person(SQLModel, table=True):
    __tablename__ = "persons"
    
    id: str = Field(primary_key=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: str = Field(index=True)
    bio: Optional[str] = Field(default=None)
    n_followers: int = Field(default=0)
    n_following: int = Field(default=0)
    n_posts: int = Field(default=0)



    # Relationships
    # One-to-many relationship with Post
    posts: List["Post"] = Relationship(back_populates="owner")

    # One-to-many relationship with Highlight
    highlights: List["Highlight"] = Relationship(back_populates="owner")

    # One-to-many relationship with Story
    stories: List["Story"] = Relationship(back_populates="owner")
