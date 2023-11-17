import sys
from pathlib import Path
from typing import Any

# import json
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
ROOT = str(root)
sys.path.append(ROOT)
from movie_model import __version__
import pandas as pd

# from skops.io import load
from data.data_validation import validate_inputs, MovieNotFoundError
from data.cosine_pipeline import COS_SIM_NAME
import logging

_logger = logging.getLogger(__name__)


def predict_movie(
    title: str,
    similarity_weight: float = 0.7,
    top_n: int = 10,
) -> Any:
    validated_input, errors = validate_inputs(input=title)
    if not errors:
        _logger.info(f"Making predictions with model version: {__version__} ")
        # Load the movies dataset and the similarity matrix
        filename_data = ROOT + "/movie_model/data/clean/final_df.parquet"
        filename_sim = ROOT + "/movie_model/data/clean/cos_sim.parquet"
        data = pd.read_parquet(
            filename_data,
            columns=["score", "id", "original_title"],
        ).reset_index()
        # Check if the movie is available before loading the similarity matrix
        if validated_input not in data["original_title"].values:
            raise MovieNotFoundError(input)
        else:
            cos_sim = pd.read_parquet(filename_sim)
            index_movie = data[data["original_title"] == "Toy Story"].index[0]
            similarity = cos_sim.values[index_movie].T
            sim_df_ = pd.DataFrame(similarity, columns=["similarity"])
            final_df = pd.concat([data, sim_df_], axis=1)
            # The number can be tinkered with
            final_df["final_score"] = (
                final_df["score"] * (1 - similarity_weight)
                + final_df["similarity"] * similarity_weight
            )
            final_df_sorted = final_df.sort_values(
                by="final_score", ascending=False
            ).head(top_n)
            final_df_sorted = final_df_sorted.drop(
                columns=["score", "similarity", "final_score"]
            ).reset_index()
            final_df_sorted.index = final_df_sorted.index + 1  # Start the index from 1

            results = final_df_sorted.rename(
                columns={"original_title": "similar_movies"}
            )[["similar_movies", "id"]].to_dict()
            results.update({"version": __version__, "errors": errors})
            # results = json.dumps(results)
            return results


print(predict_movie(title="toy Story"))
