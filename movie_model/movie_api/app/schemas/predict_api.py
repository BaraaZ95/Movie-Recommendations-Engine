from pathlib import Path
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[3]
sys.path.append(str(root))
from typing import Any, List, Optional, Dict

# from movie_model.data.data_validation import MovieInputData
from pydantic import BaseModel


class PredictionResults(BaseModel):
    errors: Optional[Any]
    version: str
    similar_movies: Optional[Any]
    id: Optional[Any]
