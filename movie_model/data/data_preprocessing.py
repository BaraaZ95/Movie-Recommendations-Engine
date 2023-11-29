from typing import List
from ast import literal_eval
import re
import string
import pandas as pd


# Captures the values from the dict keys from a string of list of dicts
def convert_str_to_list(obj: str, key: str, limit: int) -> List[str]:
    List_ = [i[key] for i in literal_eval(obj)]
    if (
        limit
    ):  # If limit specified, slice the list and take a limited number of elements
        return List_[:limit]
    else:
        return List_


def get_text(text, obj="name"):
    text = literal_eval(text)

    if len(text) == 1:
        for i in text:
            return i[obj]
    else:
        s = []
        for i in text:
            s.append(i[obj])
        return ", ".join(s)


def separate(text):
    clean_text = []
    for t in text.split(","):
        cleaned = re.sub("\(.*\)", "", t)  # type: ignore
        cleaned = cleaned.translate(str.maketrans("", "", string.digits))
        cleaned = cleaned.replace(" ", "")
        cleaned = cleaned.translate(str.maketrans("", "", string.punctuation)).lower()
        clean_text.append(cleaned)
    return " ".join(clean_text)


def remove_punctuation(text):
    cleaned = text.translate(str.maketrans("", "", string.punctuation)).lower()
    clean_text = cleaned.translate(str.maketrans("", "", string.digits))
    return clean_text


# Batches ensure it doesn't use a lot of RAM and the program runs faster and more stable
# Set batch_size to an appropriate value based on your available memory


def melt_similarity_matrix_in_batches(input_sim_df, batch_size=1000):
    similarity_matrix_df = input_sim_df.reset_index(names=["movie_id_A"])
    melted_similarity_list = []

    # Process the data in batches
    for i in range(0, len(similarity_matrix_df), batch_size):
        batch_df = similarity_matrix_df.iloc[i : i + batch_size]

        # Melt the batch
        melted_similarity_batch = pd.melt(
            batch_df,
            id_vars="movie_id_A",  # type: ignore
            var_name="movie_id_B",
            value_name="similarity_score",
        )

        # Filter out the diagonal entries where movie_id_A == movie_id_B
        melted_similarity_batch = melted_similarity_batch[
            melted_similarity_batch["movie_id_A"]
            != melted_similarity_batch["movie_id_B"]
        ]

        # Convert the similarity_score column to float32
        melted_similarity_batch["similarity_score"] = melted_similarity_batch[
            "similarity_score"
        ].astype("float32")

        melted_similarity_list.append(melted_similarity_batch)

    # Concatenate the batches into a single DataFrame
    melted_similarity = pd.concat(melted_similarity_list, ignore_index=True)

    # Change the dtypes to compress the database
    melted_similarity["movie_id_A"] = melted_similarity["movie_id_A"].astype("int32")
    melted_similarity["movie_id_B"] = melted_similarity["movie_id_B"].astype("int32")

    # Drop duplicate similarity scores. It will store smiliarity of A to B and B to A. There is no need for both values in store since both are the same.
    melted_similarity = melted_similarity[
        melted_similarity["movie_id_A"] != melted_similarity["movie_id_B"]
    ]

    # Reset the index if needed
    melted_similarity.reset_index(drop=True, inplace=True)
    return melted_similarity
