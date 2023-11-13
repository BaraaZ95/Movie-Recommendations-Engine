import sys
from pathlib import Path

from httpx import request

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[3]
sys.path.append(str(root))
from annotated_types import T

# from movie_model.data.validation import MoviePredictionInputModel
from movie_model.movie_api.app.schemas.predict_api import PredictionResults
from fastapi.encoders import jsonable_encoder
from movie_model.ml_model.predict import predict_movie
import json
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from movie_model import __version__ as model_version
from loguru import logger
from movie_model.movie_api.app import schemas

from movie_model.movie_api.app import __version__, schemas
from movie_model.movie_api.app.config import settings
from movie_model.data.data_validation import MovieInputData

api_router = APIRouter()


@api_router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> Dict:
    """
    Root Get
    """
    health = schemas.Health(
        name=settings.PROJECT_NAME, api_version=__version__, model_version=model_version
    )

    return health.dict()


@api_router.post("/predict", response_model=PredictionResults)
async def predict(response: MovieInputData) -> Any:
    """
    Make predictions with the ML model
    """
    # Advanced: You can improve performance of your API by rewriting the
    # `make prediction` function to be async and using await here.
    input_title = response.movie
    logger.info(f"Making prediction on input: {input_title}")
    results = predict_movie(title=input_title)

    if results["errors"] is not None:
        logger.warning(f"Prediction validation error: {results.get('errors')}")
        raise HTTPException(status_code=400, detail=json.loads(results["errors"]))

    logger.info(f"Prediction results: {results.get('similar_movies')}")

    return results
