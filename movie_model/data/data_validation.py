from typing import Optional
from pydantic import BaseModel, ValidationError


# Create custom error function if user inputs unavailable movie
# For better efficiency, it is best to write custom exceptions using FastAPI
class MovieNotFoundError(Exception):
    def __init__(self, input_value):
        self.input_value = input_value
        self.message = f"Movie not found for input: {input_value}"
        super().__init__(self.message)


class MovieInputData(BaseModel):
    movie: str

    # Enables the accessing of BaseModel's elements: such as accesing movie by MovieInputData.movie
    class Config:
        orm_mode = True


def validate_inputs(input: str):
    """Check model inputs for unprocessable values."""
    # Convert the input text to the correct format
    input_data = str(input).title().strip()

    errors = None

    try:
        MovieInputData(movie=input_data)
    except ValidationError as exc:
        errors = exc.json()

    return input_data, errors
