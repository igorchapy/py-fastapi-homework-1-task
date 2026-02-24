from datetime import date
from typing import List

from pydantic import BaseModel


class MovieBase(BaseModel):
    name: str
    date: date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str


class MovieCreate(MovieBase):
    pass


class MovieDetailResponseSchema(MovieBase):
    id: int

    class Config:
        from_attributes = True


class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailResponseSchema]
    prev_page: str | None = None
    next_page: str | None = None
    total_pages: int
    total_items: int
