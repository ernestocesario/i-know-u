from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .person import Person
    from .content import Content


class Story(SQLModel, table=True):
    __tablename__ = "stories"

    id: Optional[int] = Field(default=None, primary_key=True)

    publication_date: date = Field()
    processed: bool = Field(default=False)



    # Relationships
    # Many-to-one relationship with Person
    owner_id: str = Field(foreign_key="persons.id")
    owner: Person = Relationship(back_populates="stories")

    # One-to-many relationship with Content
    contents: list[Content] = Relationship(back_populates="story")