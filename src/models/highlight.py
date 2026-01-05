from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from . import Content
    from .person import Person


class Highlight(SQLModel, table=True):
    __tablename__ = "highlights"

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)

    title: str = Field()

    # calculated by AI models
    inference_summary: Optional[str] = Field(default=None)



    # Relationships
    # Many-to-one relationship with Person
    owner_id: int = Field(foreign_key="persons.id")
    owner: Person = Relationship(back_populates="highlights")

    # One-to-many relationship with Content
    contents: list[Content] = Relationship(back_populates="highlight")