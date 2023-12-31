import os
from dotenv import load_dotenv

# from movie_model.data.validation import MoviePredictionInputModel
from app.schemas.items import SimilarMovie
from typing import Dict, Any

from app.schemas.health import Health
from app.schemas.items import MovieInput

from app import __version__
from app.config import settings

# from data.data_validation import MovieInputData
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase
from app.models import Movie


@asynccontextmanager
async def lifespan_db(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


api_router = APIRouter()
app = FastAPI(lifespan=lifespan_db)


class Base(DeclarativeBase):
    pass


@api_router.get("/health", response_model=Health, status_code=200)
def health() -> Dict:
    """
    Root Get
    """
    health = Health(name=settings.PROJECT_NAME, api_version=__version__)

    return dict(health)


# Initialize environment variables
load_dotenv()

# PostgreSQL connection string
dialect = os.getenv("dialect")
host = os.getenv("host")
port = os.getenv("port")
database = os.getenv("database")
username = os.getenv("username")
password = os.getenv("password")
engine = create_engine(f"{dialect}://{username}:{password}@{host}:{port}/{database}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Function to get a database session
def get_db() -> Session:  # type: ignore
    db = SessionLocal()
    try:
        yield db  # type: ignore
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


class MovieOutput:
    original_title: str


# Function to get movie index from movie name
# @app.get("/get_movie_index/{movie_name}")
def get_movie_index(movie_name: str, db: Session = Depends(get_db)):  # type: ignore
    movie = db.query(Movie).filter(Movie.original_title == movie_name).first()
    if movie:
        return movie.movie_index
    raise HTTPException(status_code=404, detail="Movie not found!")


@api_router.post(path="/predict", response_model=list[SimilarMovie])
async def get_similar_movies_dict(
    response: MovieInput, db: Session = Depends(get_db)  # type: ignore
) -> Any:
    input_movie_name = response.movie
    # Use a database session to get the movie_index from the movie name
    movie_index = get_movie_index(input_movie_name, db)
    if movie_index is None:
        return {
            "error": "Movie not found. Cannot establish connection to similarity matrix db when movie unknown!"
        }
    sql = """
   -- Select the other_movie_index, similarity_score, and other_movie_name, along with id
SELECT
    CASE
        WHEN sim.movie_id_A = :input_movie_id THEN sim.movie_id_B
        ELSE sim.movie_id_A
    END AS movie_index,
    sim.similarity_score,
    movies.original_title AS other_movie_name,
    movies.id AS imdb_id
FROM
    sim_matrix sim
-- Join the sim_matrix table with the movies table
JOIN
    movies ON (CASE WHEN sim.movie_id_A = :input_movie_id THEN sim.movie_id_B ELSE sim.movie_id_A END) = movies.movie_index
-- Filter the rows where movie_id_A or movie_id_B is :input_movie_id
WHERE
    :input_movie_id IN (sim.movie_id_A, sim.movie_id_B)
ORDER BY
    sim.similarity_score DESC
-- Limit the result to the top 10 rows
LIMIT 10;
        """
    with engine.connect() as connection:
        result = connection.execute(text(sql).bindparams(input_movie_id=movie_index))
        rows = result.fetchall()
    # Convert the result to a list of dictionaries
    # Ensure rows are not empty
    if not rows:
        return []

    # Assuming rows are named tuples, convert them to dictionaries
    row_dicts = [dict(row._asdict()) for row in rows]

    return row_dicts
