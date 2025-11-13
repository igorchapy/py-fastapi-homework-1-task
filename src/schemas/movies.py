# Write your code here
import datetime
from typing import List, Optional

from pydantic import BaseModel


class MovieBase(BaseModel):
    id: int
    name: str
    date: datetime.date
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

    class Config:
        from_attributes = True


class MovieListResponseSchema(MovieBase):
    pass


class MovieDetailResponseSchema(MovieBase):
    pass


class PaginatedMoviesResponse(BaseModel):
    movies: List[MovieListResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int
