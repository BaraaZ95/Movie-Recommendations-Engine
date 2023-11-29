from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
ROOT = str(root)
sys.path.append(ROOT)
from movie_api.app.api import get_db  # noqa: E402
from movie_api.main import app  # noqa: E402
from movie_api.app.config import settings  # noqa: E402


openapi_url = f"{settings.API_V1_STR}"
# Setup the TestClient
client = TestClient(app)


# Setup the in-memory Postgresql database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


# Test if the api is accepting input
def test_get_movie_index():
    movie_name = "Toy Story"
    response = client.post(f"{openapi_url}/predict", json={"movie": movie_name})
    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)  # It is returning a list of similar movies
