import os
from dotenv import load_dotenv
import streamlit as st
import json
from preprocessing import contains_non_english
import requests
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from sqlalchemy import create_engine
from sqlalchemy import text


st.set_page_config(layout="wide")
# Function to check if a string contains non-English letters

# Initialize environment variables
load_dotenv()
api_key = os.getenv("IMDB_API_KEY")  # For imdb movies posters

# PostgreSQL connection string
dialect = os.getenv("dialect")
host = os.getenv("host")
port = os.getenv("port")
database = os.getenv("database")
username = os.getenv("username")
password = os.getenv("password")

postgres_conn_str = f"{dialect}://{username}:{password}@{host}:{port}/{database}"


# Initialize connection.
@st.cache_data()  # 👈 Add the caching decorator
def load_movies():
    engine = create_engine(postgres_conn_str)
    query = text(
        """
    SELECT original_title FROM movies 
    ORDER BY original_title ASC;
    """
    )
    with engine.connect() as connection:
        result = connection.execute(query)
        movies = [row[0] for row in result.fetchall() if contains_non_english(row[0])]
    return movies


# Loading the movies makes sure the input is only from the database, so no need for data validation from the backend
movies = load_movies()
load_dotenv()
api_key = os.getenv("IMDB_API_KEY")

print(f"THE api_key is {api_key}")


def fetch_poster(movie_id):
    headers = {"Accept-Encoding": "gzip"}
    session = CacheControl(requests.Session(), cache=FileCache(".web_cache"))

    response = session.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}",
        headers=headers,
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]


# ''' Frontend '''

v = st.write(
    """ <h2> <b style="color:red"> Movie Recommendations Engine</b> </h2>""",
    unsafe_allow_html=True,
)
st.write("###")

st.write(
    """ <p> Hi, welcome to my  <b style="color:red">Movie Recommendations Engine</b> </p>""",
    unsafe_allow_html=True,
)
st.write("##")
my_expander = st.expander("Tap to Select a Movie  🍿")
selected_movie_name = my_expander.selectbox("Type movie name", movies)


if my_expander.button("Recommend"):
    st.text("Here are few Recommendations..")
    st.write("#")
    st.write(f"Similar movies to {selected_movie_name}: ")
    res = requests.post(
        url="http://api:8001/api/v1/predict",
        data=json.dumps({"movie": selected_movie_name}),
    )
    response_received = res.json()
    names = [i.get("other_movie_name") for i in response_received]
    movie_ids = [i.get("imdb_id") for i in response_received]
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
