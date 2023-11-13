import typing as t

import numpy as np
import pandas as pd
from pydantic import BaseModel, ValidationError


def validate_inputs(*, input: str):
    """Check model inputs for unprocessable values."""
    errors = None
    try:
        MoviePredictionInputModel(movie=input)
    except ValidationError as exc:
        errors = exc.json()

    return input, errors


class MoviePredictionInputModel(BaseModel):
    movie: t.Optional[str]

    class Config:
        schema_extra = {"movie": "Toy Story"}
        orm_mode = True
