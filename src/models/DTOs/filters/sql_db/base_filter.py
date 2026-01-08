from typing import Optional
from sqlmodel import SQLModel


class BaseFilter(SQLModel):
    # Pagination
    limit: Optional[int] = None
    offset: Optional[int] = None

    # Sorting
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"  # "asc" or "desc"