import pytest
from sqlalchemy import create_engine, text, StaticPool
from sqlalchemy.orm import sessionmaker
from faker import Faker
from fastapi.testclient import TestClient
from pathlib import Path
import os
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
ROOT = str(root)
sys.path.append(ROOT)

from movie_api.app.api import get_db
from movie_api.app.api import get_movie_index
from movie_api.main import app  # noqa: E402
from movie_api.app.config import settings  # noqa: E402
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Create a fake similarity matrix and movies for teseting the database
class SimMatrix(Base):
    __tablename__ = "sim_matrix"
    index = Column(Integer, primary_key=True, index=True)
    movie_id_A = Column(Integer)
    movie_id_B = Column(Integer)
    similarity_score = Column(Float)


class Movie(Base):
    __tablename__ = "movies"
    index = Column(Integer, primary_key=True, index=True)
    movie_index = Column(Integer)
    original_title = Column(String)
    id = Column(Integer)


openapi_url = f"{settings.API_V1_STR}"
# Setup the TestClient
client = TestClient(app)
# Import your actual functions

DATABASE_URL = "sqlite:///:memory:"  # Use an in-memory Postgresql database for testing

# Initialize a test database
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

fake = Faker()


def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def db():
    connection = engine.connect()
    transaction = connection.begin()

    # Use the testing database during the test
    session = TestingSessionLocal()

    # Create the necessary tables
    Base.metadata.create_all(bind=engine)

    yield session

    # Rollback the transaction after the test
    session.close()
    transaction.rollback()
    connection.close()


def create_fake_data(db, num_records=20):
    """
    Create fake data (similarity_matrix) for testing.
    """
    # Create the necessary tables
    Base.metadata.create_all(bind=engine)
    for _ in range(num_records):
        if _ == 10:
            movie_name = "Toy Story"
        else:
            movie_name = fake.word()
        movie_id_A = fake.random_int(min=1, max=num_records)
        movie_id_B = fake.random_int(min=1, max=num_records)
        similarity_score = fake.pyfloat(min_value=0, max_value=1)

        # Print information about the data being inserted
        print(
            f"Inserting data into sim_matrix: {movie_id_A}, {movie_id_B}, {similarity_score}"
        )

        db.execute(
            text(
                "INSERT INTO sim_matrix (movie_id_A, movie_id_B, similarity_score) "
                "VALUES (:movie_id_A, :movie_id_B, :similarity_score)"
            ),
            {
                "movie_id_A": movie_id_A,
                "movie_id_B": movie_id_B,
                "similarity_score": similarity_score,
            },
        )

        print(f"Inserting data into movies: {movie_id_A}, {movie_name}")
        db.execute(
            text(
                "INSERT INTO movies (movie_index, original_title, id) "
                "VALUES (:movie_index, :original_title, :imdb_id)"
            ),
            {
                "movie_index": movie_id_A,
                "original_title": movie_name,
                "imdb_id": fake.uuid4(),
            },
        )

        print(f"Inserting data into movies: {movie_id_B}, {movie_name}")
        db.execute(
            text(
                "INSERT INTO movies (movie_index, original_title, id) "
                "VALUES (:movie_index, :original_title, :imdb_id)"
            ),
            {
                "movie_index": movie_id_B,
                "original_title": movie_name,
                "imdb_id": fake.uuid4(),
            },
        )


def test_get_similar_movies_dict(db):
    create_fake_data(db)
    movie = "Toy Story"

    # Get Toy Story's movie index
    movie = db.query(Movie).filter(Movie.original_title == movie).first()

    print(movie)

    sql = """
    SELECT
        CASE
            WHEN sim.movie_id_A = :movie_index THEN sim.movie_id_B
            ELSE sim.movie_id_A
        END AS movie_index,
        sim.similarity_score,
        movies.original_title AS other_movie_name,
        movies.id AS imdb_id
    FROM
        sim_matrix sim
    JOIN
        movies ON (CASE WHEN sim.movie_id_A = :movie_index THEN sim.movie_id_B ELSE sim.movie_id_A END) = movies.movie_index
    WHERE
        :movie_index IN (sim.movie_id_A, sim.movie_id_B)
    ORDER BY
        sim.similarity_score DESC
    LIMIT 10;
    """

    with engine.connect() as connection:
        result = connection.execute(text(sql).bindparams(movie_index=movie.movie_index))
        rows = result.fetchall()

    # Convert the result to a list of dictionaries
    final_result = [dict(row._asdict()) for row in rows]
    print(final_result)

    for item in final_result:
        assert "movie_index" in item
        assert "similarity_score" in item
        assert "other_movie_name" in item
        assert "imdb_id" in item
