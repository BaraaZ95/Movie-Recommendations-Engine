import sys
from pathlib import Path
import os

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
import streamlit as st

import requests
import pandas as pd
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from loguru import logger

from movie_api.app import __version__
from movie_api.app.config import settings

st.set_page_config(layout="wide")


@st.cache_data(persist="disk")
def load_movies():
    filepath = str(root) + r"\data\clean\final_df.parquet"
    loaded_movies = pd.read_parquet(filepath, columns=["original_title"])
    return loaded_movies["original_title"].values


movies = load_movies()

api_key = os.getenv("API_KEY")


def fetch_poster(movie_id):
    headers = {"Accept-Encoding": "gzip"}
    session = CacheControl(requests.Session(), cache=FileCache(".web_cache"))

    response = session.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}",
        headers=headers,
    )
    data = response.json()
    # print(data)
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]


# ''' Frontend '''

v = st.write(
    """ <h2> <b style="color:red"> Movie Recommendations Engine</b> </h2>""",
    unsafe_allow_html=True,
)
# st.header(v)
# st.header(" :red[MoviesWay]")
st.write("###")

st.write(
    """ <p> Hi, welcome to <b style="color:red">Movie Recommendations Engine</b> Mh free movie recommendation engine </p>""",
    unsafe_allow_html=True,
)
st.write("##")
my_expander = st.expander("Tap to Select a Movie  🍿")
selected_movie_name = my_expander.selectbox("Type movie name", movies)

import json

if my_expander.button("Recommend"):
    st.text("Here are few Recommendations..")
    st.write("#")
    st.write(f"Movie selected is {selected_movie_name}")
    res = requests.post(
        url="http://127.0.0.1:8000/api/v1/predict",
        data=json.dumps({"movie": selected_movie_name}),
    )
    response_received = res.json()
    print(response_received)
    names = [i for i in response_received.get("similar_movies").values()]
    movie_ids = [i for i in response_received.get("id").values()]
    posters = [fetch_poster(i) for i in movie_ids]

    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
    cols = [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10]
    for i in range(0, 10):
        with cols[i]:
            st.write(
                f' <b style="color:#E50914"> {names[i]} </b>', unsafe_allow_html=True
            )
            # st.write("#")
            st.image(posters[i])
            id = movie_ids[i]
