import pandas as pd
from .data_preprocessing import get_text, remove_punctuation, separate
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# from skops.io import dump
import joblib

_logger = logging.getLogger(__name__)


FINAL_DF_NAME = "final_df.parquet"
COS_SIM_NAME = "cos_sim.parquet"  # or skops can be used


# Load the datasets

_logger.info("Loading the dataset")


def prepare_data():
    credits = pd.read_csv("movie_model/data/raw/credits.csv")
    keywords = pd.read_csv("movie_model/data/raw/keywords.csv")
    movies = (
        pd.read_csv("movie_model/data/raw/movies_metadata.csv", low_memory=False)
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

    movies["id"] = movies["id"].astype("int64")

    df = movies.merge(keywords, on="id").merge(credits, on="id")

    df["original_language"] = df["original_language"].fillna("")
    df["runtime"] = df["runtime"].fillna(0)
    df["tagline"] = df["tagline"].fillna("")

    df.dropna(inplace=True)

    df["genres"] = df["genres"].apply(get_text)
    df["production_companies"] = df["production_companies"].apply(get_text)
    df["production_countries"] = df["production_countries"].apply(get_text)
    df["crew"] = df["crew"].apply(get_text)
    df["spoken_languages"] = df["spoken_languages"].apply(get_text)
    df["keywords"] = df["keywords"].apply(get_text)

    # New columns
    df["characters"] = df["cast"].apply(get_text, obj="character")
    df["actors"] = df["cast"].apply(get_text)

    df.drop("cast", axis=1, inplace=True)
    df = df[~df["original_title"].duplicated()]
    df = df.reset_index(drop=True)

    df["release_date"] = pd.to_datetime(df["release_date"])
    df["budget"] = df["budget"].astype("float64")
    df["popularity"] = df["popularity"].astype("float64")

    # Take the weighted average based on the vote count =
    # ( Ratings(R) * Votes count(v) + Mean Vote(C) * Minimum required votes(m)) / (Votes count (v) * Minimum votes required (m) )
    R = df["vote_average"]
    v = df["vote_count"]
    # We will only consider movies that have more votes than at least 80% of the movies in our dataset
    m = df["vote_count"].quantile(0.8)
    C = df["vote_average"].mean()

    df["weighted_average"] = (R * v + C * m) / (v + m)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["popularity", "weighted_average"]])
    weighted_df = pd.DataFrame(scaled, columns=["popularity", "weighted_average"])

    weighted_df.set_index(df["original_title"], inplace=True)
    # score column will reflect the movie's score is based 60% on its popularity and 40% on the weighted average vote as
    # a movie's popularity is more important than the reviews
    weighted_df["score"] = (
        weighted_df["weighted_average"] * 0.4
        + weighted_df["popularity"].astype("float64") * 0.6
    )

    # Index and sort based on the movie
    weighted_df_sorted = weighted_df.sort_values(by="score", ascending=False)

    final_df = df[
        [
            "original_title",
            "adult",
            "genres",
            "overview",
            "production_companies",
            "tagline",
            "keywords",
            "crew",
            "characters",
            "actors",
        ]
    ]

    final_df.loc[:, "adult"] = final_df["adult"].apply(remove_punctuation)
    final_df.loc[:, "genres"] = final_df["genres"].apply(remove_punctuation)
    final_df.loc[:, "overview"] = final_df["overview"].apply(remove_punctuation)
    final_df.loc[:, "production_companies"] = final_df["production_companies"].apply(
        separate
    )
    final_df.loc[:, "tagline"] = final_df["tagline"].apply(remove_punctuation)
    final_df.loc[:, "keywords"] = final_df["keywords"].apply(separate)
    final_df.loc[:, "crew"] = final_df["crew"].apply(separate)
    final_df.loc[:, "characters"] = final_df["characters"].apply(separate)
    final_df.loc[:, "actors"] = final_df["actors"].apply(separate)

    final_df.loc[:, "bag_of_words"] = ""
    final_df.loc[:, "bag_of_words"] = final_df[final_df.columns[1:]].apply(
        lambda x: " ".join(x), axis=1
    )
    final_df.set_index("original_title", inplace=True)

    final_df = final_df[["bag_of_words"]]
    final_df = weighted_df_sorted[:10000].merge(
        final_df, left_index=True, right_index=True, how="left"
    )
    # Calculate cosine similary between the movies. The df can be sliced to reduce the extensiveness of the resources
    # Add the id to the df to use it to retrive its info from the api
    tfidf = TfidfVectorizer(stop_words="english", min_df=5)
    tfidf_matrix = tfidf.fit_transform(final_df["bag_of_words"])
    cos_sim = cosine_similarity(tfidf_matrix)
    cos_sim_df = pd.DataFrame(cos_sim).T
    cos_sim_df.to_parquet(f"movie_model/data/clean/{COS_SIM_NAME}", index=False)
    _logger.info(f"Saving the dataset as {FINAL_DF_NAME}")
    final_df.to_parquet(f"movie_model/data/clean/{FINAL_DF_NAME}", index=False)
