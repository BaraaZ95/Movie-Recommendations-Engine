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
COS_SIM_NAME = "cos_sim.pkl"  # or skops can be used


# Load the datasets

_logger.info("Loading the dataset")


def prepare_data():
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

    ## Data Engineering Validations ##
    # Merge movies with credits
    movies["id"] = movies["id"].astype("int64")

    df = movies.merge(keywords, on="id").merge(credits, on="id")

    # Fill missing values
    df["original_language"] = df["original_language"].fillna("")
    df["runtime"] = df["runtime"].fillna(0)
    df["tagline"] = df["tagline"].fillna("")

    df.dropna(inplace=True)

    _logger.info("Cleaning the dataset")

    # clean the text and convert json to list
    df["genres"] = df["genres"].apply(get_text)
    df["production_companies"] = df["production_companies"].apply(get_text)
    df["production_countries"] = df["production_countries"].apply(get_text)
    df["crew"] = df["crew"].apply(get_text)
    df["spoken_languages"] = df["spoken_languages"].apply(get_text)
    df["keywords"] = df["keywords"].apply(get_text)

    # Create new columns
    df["characters"] = df["cast"].apply(get_text, obj="character")
    df["actors"] = df["cast"].apply(get_text)

    df.drop("cast", axis=1, inplace=True)
    df = df[~df["original_title"].duplicated()]
    df = df.reset_index(drop=True)

    # Assign the right types to each column
    df["release_date"] = pd.to_datetime(df["release_date"])
    df["budget"] = df["budget"].astype("float64")
    df["popularity"] = df["popularity"].astype("float64")

    # Take the weighted average based on the vote count =
    # ( Ratings(R) * Votes count(v) + Mean Vote(C) * Minimum required votes(m)) / (Votes count (v) * Minimum votes required (m) )
    R = df["vote_average"]
    v = df["vote_count"]
    # We will only consider movies that have more votes than at least 70% of the movies in our dataset
    m = df["vote_count"].quantile(0.7)
    C = df["vote_average"].mean()

    df["weighted_average"] = (R * v + C * m) / (v + m)

    _logger.info("Applying transformations to the dataset")
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["popularity", "weighted_average"]])
    weighted_df = pd.DataFrame(scaled, columns=["popularity", "weighted_average"])

    weighted_df = weighted_df.set_index(df["original_title"])

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
            "id",
        ]
    ]
    final_df["adult"] = final_df["adult"].apply(remove_punctuation)
    final_df["genres"] = final_df["genres"].apply(remove_punctuation)
    final_df["overview"] = final_df["overview"].apply(remove_punctuation)
    final_df["production_companies"] = final_df["production_companies"].apply(separate)
    final_df["tagline"] = final_df["tagline"].apply(remove_punctuation)
    final_df["keywords"] = final_df["keywords"].apply(separate)
    final_df["crew"] = final_df["crew"].apply(separate)
    final_df["characters"] = final_df["characters"].apply(separate)
    final_df["actors"] = final_df["actors"].apply(separate)

    final_df["bag_of_words"] = ""
    final_df["bag_of_words"] = final_df[final_df.columns[1:]].apply(
        lambda x: " ".join(x), axis=1
    )
    final_df.set_index("original_title", inplace=True)
    final_df = final_df[["bag_of_words"]]

    # Calculate cosine similary between the movies. The df can be sliced to reduce the extensiveness of the resources
    final_df = weighted_df_sorted.iloc[:10000].merge(
        final_df, left_index=True, right_index=True, how="left"
    )
    # Add the id to the df to use it to retrive its info from the api
    final_df = pd.merge(
        final_df.reset_index(), df[["original_title", "id"]], on=["original_title"]
    )
    # Save the final df
    _logger.info(f"Saving the dataset as {FINAL_DF_NAME}")
    final_df.to_parquet(f"ml_model/data/clean/{FINAL_DF_NAME}", index=False)
    # or final_df.to_parquet(FINAL_DF_NAME, index= False)
    tfidf = TfidfVectorizer(stop_words="english", min_df=5)
    tfidf_matrix = tfidf.fit_transform(final_df["bag_of_words"])
    cos_sim = cosine_similarity(tfidf_matrix)
    joblib.dump(cos_sim, f"ml_model/data/clean/{COS_SIM_NAME}")
    # dump(cos_sim, "COS_SIM_NAME.skops") #or using skops for more security
