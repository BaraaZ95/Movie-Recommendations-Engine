from pydantic import BaseModel, Field, ConfigDict

# from movie_model.data.data_validation import MovieInputData


class MovieInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    movie: str = Field(examples=["Toy Story"])


class SimilarMovie(BaseModel):
    # The actual similarity scores and movie indexes can be ommited as it is not used in the frontend
    other_movie_name: str = Field(examples=["Toy Story 2"])
    movie_index: int = Field(examples=[461])
    similarity_score: float = Field(examples=[0.53732014])
    imdb_id: int = Field(examples=[863])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "movie_index": 461,
                    "similarity_score": 0.53732014,
                    "other_movie_name": "Toy Story 2",
                    "imdb_id": 863,
                },
                {
                    "movie_index": 1514,
                    "similarity_score": 0.29485983,
                    "other_movie_name": "Toy Story of Terror!",
                    "imdb_id": 213121,
                },
                {
                    "movie_index": 223,
                    "similarity_score": 0.27477807,
                    "other_movie_name": "Toy Story 3",
                    "imdb_id": 10193,
                },
            ]
        }
    }
