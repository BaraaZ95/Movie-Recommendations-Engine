import os
import wandb
import pandas as pd

## Wandb can be incorporated directly into the cosine_pipeline during the preprocessing steps##


def load():
    credits = pd.read_csv("ml_model/data/raw/credits.csv")
    keywords = pd.read_csv("ml_model/data/raw/keywords.csv")
    movies = (
        pd.read_csv("ml_model/data/raw/movies_metadata.csv", low_memory=False)
        .drop(
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
        .drop([19730, 29503, 35587])
    )  # Incorrect data type

    datasets = [credits, keywords, movies]

    return datasets


def load_and_log():
    # 🚀 start a run, with a type to label it and a project it can call home
    with wandb.init(project="movies-project", job_type="load-data") as run:
        # Start a W&B run to log data
        datasets = load()  # separate code for loading the datasets
        names = ["credits", "keywords", "movie"]
        movie_table_artifact = wandb.Artifact(
            "movies_artifact",
            type="dataset",
            description="Raw MNIST dataset, split into train/val/test",
            metadata={
                "source": "imdb",
                "sizes": [len(dataset) for dataset in datasets],
            },
        )
        # Convert the DataFrame into a W&B Table
        for name, dataset in zip(names, datasets):
            wandb_table = wandb.Table(dataframe=dataset)
            movie_table_artifact.add(wandb_table, f"{name}_table")
            # Log the table to visualize with a run...
            run.log({f"{name}": wandb_table})

            # Log the raw csv file within an artifact to preserve our data
            movie_table_artifact.add(dataset, f"{name}-dataset")

            # Add the cosine similarity matrix
            cos_sim = pd.read_csv("ml_model/data/raw/cos_sim.pkl")
            movie_table_artifact.add(cos_sim, "cos_sim")

        # Finish the run (useful in notebooks)
        run.finish()
