from __future__ import annotations

from math import ceil
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=200)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)

    @classmethod
    def build(cls, *, items: List[T], page: int, size: int, total: int):
        pages = ceil(total / size) if size > 0 else 0
        return cls(items=items, page=page, size=size, total=total, pages=pages)