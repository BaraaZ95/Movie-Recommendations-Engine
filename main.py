# import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.params import Depends
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Integer, String, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

app = FastAPI()


class MovieID(BaseModel):
    movie_id: int


host = "172.17.42.151"
port = 5433
database = "test"
user = "postgres"
password = "pass"

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# database_url = os.environ.get("DATABASE_URL")
# engine = create_engine(database_url)
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


class MovieNameInput(BaseModel):
    movie_name: str


class MovieOutput:
    original_title: str


class Movie(Base):
    __tablename__ = "movies"
    movie_index: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_title: Mapped[str] = mapped_column(String(30))
    id: Mapped[int] = mapped_column(
        Integer
    )  # IMDB id used to retrieve artwork and other information


# Function to get movie index from movie name
# @app.get("/get_movie_index/{movie_name}")
def get_movie_index(movie_name: str, db: Session = Depends(get_db)):  # type: ignore
    # db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    movie = db.query(Movie).filter(Movie.original_title == movie_name).first()
    if movie:
        return movie.movie_index
    raise HTTPException(status_code=404, detail="Movie not found")


async def get_similar_movies_dict(
    movie_input: MovieNameInput, db: Session = Depends(get_db)  # type: ignore
):
    input_movie_name = movie_input.movie_name
    # Use a database session to get the movie_index from the movie name
    print(input_movie_name)

    movie_index = get_movie_index(input_movie_name, db)
    print(movie_index)
    if movie_index is None:
        return {"error": "Movie not found"}
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
