import random
import pytest
from sqlalchemy import select, func
from database import MovieModel  # Make sure you only import once from the correct place
from src.database import MovieModel


@pytest.mark.asyncio
async def test_get_movies_with_custom_parameters(client, seed_database):
    page = 2
    per_page = 5

    response = await client.get(f"/api/v1/theater/movies/?page={page}&per_page={per_page}")
    assert response.status_code == 200

    response_data = response.json()
    assert "movies" in response_data
    assert len(response_data["movies"]) <= per_page


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page, per_page, expected_detail",
    [
        (0, 10, "Input should be greater than or equal to 1"),
        (1, 0, "Input should be greater than or equal to 1"),
        (0, 0, "Input should be greater than or equal to 1"),
    ],
)
async def test_invalid_page_and_per_page(client, page, per_page, expected_detail):
    """
    Test invalid pagination parameters.
    Expected:
        - 422 response status code.
        - JSON validation error with the expected message.
    """
    response = await client.get(f"/api/v1/theater/movies/?page={page}&per_page={per_page}")
    assert response.status_code == 422

    response_data = response.json()
    assert "detail" in response_data
    assert expected_detail in response_data["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_max_per_page_limit(client):
    """
    Test that the maximum per_page is 20.
    Expected:
        - 200 response status code.
        - A maximum of 20 movies in the response.
    """
    response = await client.get("/api/v1/theater/movies/?page=1&per_page=20")
    assert response.status_code == 200
    response_data = response.json()
    assert "movies" in response_data
    assert len(response_data["movies"]) <= 20


@pytest.mark.asyncio
async def test_page_exceeds_maximum(client, db_session, seed_database):
    """
    Test retrieving a page number that exceeds the total available pages.
    Expected:
        - 404 response status code.
        - JSON response with a "No movies found." error.
    """
    per_page = 10
    total_movies = await db_session.scalar(select(func.count()).select_from(MovieModel))
    max_page = (total_movies + per_page - 1) // per_page

    response = await client.get(f"/api/v1/theater/movies/?page={max_page + 1}&per_page={per_page}")
    assert response.status_code == 404
    assert response.json()["detail"] == "No movies found."


@pytest.mark.asyncio
async def test_get_movie_by_id_not_found(client):
    """
    Test retrieving a movie by an ID that does not exist.
    Expected:
        - 404 response status code.
        - JSON response with a "Movie with the given ID was not found." error.
    """
    movie_id = 1
    response = await client.get(f"/api/v1/theater/movies/{movie_id}/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie with the given ID was not found."}


@pytest.mark.asyncio
async def test_get_movie_by_id_valid(client, db_session, seed_database):
    """
    Test retrieving a valid movie by ID.
    Expected:
        - 200 response status code.
        - JSON response containing the correct movie details.
    """
    min_id = (
        await db_session.execute(select(MovieModel.id).order_by(MovieModel.id.asc()))
    ).scalars().first()
    max_id = (
        await db_session.execute(select(MovieModel.id).order_by(MovieModel.id.desc()))
    ).scalars().first()

    random_id = random.randint(min_id, max_id)
    expected_movie = await db_session.get(MovieModel, random_id)

    response = await client.get(f"/api/v1/theater/movies/{random_id}/")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == expected_movie.id
    assert response_data["title"] == expected_movie.title
    # Add more assertions based on your movie model fields