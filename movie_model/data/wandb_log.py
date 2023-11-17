import wandb
import pandas as pd

## Wandb can be incorporated directly into the cosine_pipeline during the preprocessing steps##


def load():
    credits = pd.read_csv("movie_model/data/raw/credits.csv")
    keywords = pd.read_csv("movie_model/data/raw/keywords.csv")
    movies = (
        pd.read_csv("movie_model/data/raw/movies_metadata.csv", low_memory=False).drop(
            [
                "belongs_to_collection",
                "homepage",
                "imdb_id",
                "poster_path",
                "status",
                "title",
                "video",
            ],
            axis=1,
        )
    ).dropna(subset=["tagline"])

    datasets = [credits, keywords, movies]

    return datasets


def load_and_log():
    # 🚀 start a run, with a type to label it and a project it can call home
    wandb.init(project="movies-project", job_type="load-data")

    datasets = load()  # separate code for loading the datasets
    names = ["credits", "keywords", "movie"]

    # Convert the DataFrame into a W&B Table
    for name, dataset in zip(names, datasets):
        artifact_name = f"{name}"
        artifact = wandb.Artifact(
            artifact_name,
            type="dataset",
            metadata={"source": "imdb", "size": dataset.shape},
            description="Movies details datasets",
        )
        wandb_table = wandb.Table(dataframe=dataset)
        # Log the raw csv file within an artifact to preserve our data
        artifact.add(wandb_table, f"{name}-dataset")
        # Log the table to visualize with a run...
        wandb.log_artifact(artifact)

    # Finish the run (useful in notebooks)
    wandb.finish()
