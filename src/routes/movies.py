from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, MovieModel


router = APIRouter()

@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movie(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (>= 1)"),
    per_page: int = Query(10, ge=1, le=20, description="Items per page(1–20)"),
    db: AsyncSession = Depends(get_db),
):
    # Calculate offset
    offset = (page - 1) * per_page

    # Total number of movies
    total_items = await db.scalar(select(func.count()).select_from(MovieModel))

    if total_items == 0 or offset >= total_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found.",
        )

    # Query the movies for the current page
    stmt = (
        select(MovieModel)
        .offset(offset)
        .limit(per_page)
        .order_by(MovieModel.id)
    )
    result = await db.scalars(stmt)
    movies = result.all()

    # Calculate pagination
    total_pages = ceil(total_items / per_page)

    base_url = str(request.url).split("?")[0]  # /movies/
    prev_page = f"{base_url}?page={page - 1}&per_page={per_page}"\
        if page > 1 else None
    next_page = f"{base_url}?page={page + 1}&per_page={per_page}"\
        if page < total_pages else None

    # Return wrapped response
    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_details(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found.",
        )

    return movie
