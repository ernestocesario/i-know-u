from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .person import Person
    from .content import Content


class Highlight(SQLModel, table=True):
    __tablename__ = "highlights"

    id: str = Field(primary_key=True, index=True)
    title: str = Field()

    # calculated by AI models
    inference_summary: Optional[str] = Field(default=None)



    # Relationships
    # Many-to-one relationship with Person
    owner_id: str = Field(foreign_key="persons.id")
    owner: Person = Relationship(back_populates="highlights")

    # One-to-many relationship with Content
    contents: list[Co8ntent] = Relationship(back_populates="highlight")