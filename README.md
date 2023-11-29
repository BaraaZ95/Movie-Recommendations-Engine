# MLOPs Recommendation Engine
## Overview

This project is a web-based recommendation engine application that utilizes the cosine similarity algorithm. The application is built with a backend powered by FastAPI, a frontend developed with Streamlit, and containerized using Docker Compose. The data for the recommendation system is logged to Weights and Biases, and the similarity matrix is stored in a PostgreSQL database.


## Prerequisites

Make sure you have the following prerequisites installed:

- Docker
- Docker Compose
- Python 3.10
- pip (Python package installer)
- Postgreql

## Installation

Clone the repository and install the Python dependencies. 

Configuration

Set up your configuration by modifying the .env file:

ini

.env environment variables
```
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_database
POSTGRES_HOST = your_postgres_host
WANDB_API_KEY=your_weights_and_biases_api_key
```
Usage

The web app cannot be instantly launched since I am have a ver large csv file of the similarity matrix (10000 x 10000).

To replicate the project, you will need to retrain the similarity matrix.

Just go to `train_model.py` and run it. It will automatically load the dataset, clean the data and write it to postgresql. Then you are good to go.

After obtaining the similarity matrix:

`bash
docker-compose up --build`

Visit http://localhost:8501 in your web browser to access the recommendation engine web app.

Data Flow

    Cosine Similarity Algorithm:
        The recommendation system algorithm used is cosine similarity.
        Data is logged to Weights and Biases for analysis.

    PostgreSQL Database:
        The data for the similarity matrix and the movies dataset are stored in a PostgreSQL database.

    FastAPI Backend:
        The backend, powered by FastAPI, retrieves data from the PostgreSQL database.
        Endpoints are available to query the similarity matrix and the movie imdb_ids for getting the posters for the frontend.

    Streamlit Frontend:
        The frontend is developed using Streamlit.
        Users interact with the recommendation system through the Streamlit app.

Logging

Data is logged to Weights and Biases for monitoring and analysis. Use the Weights and Biases dashboard to gain insights into the recommendation system's performance and behavior.
Backend

The backend is built with FastAPI, providing a RESTful API to interact with the recommendation system. Key endpoints include:

    /api/similarity-matrix: Retrieve the similarity matrix data.

Frontend

The frontend is developed using Streamlit, offering a user-friendly interface for users to interact with the recommendation system.
Docker Compose

The entire application is containerized using Docker Compose. The docker-compose.yml file defines the services and their configurations.

Testing

Separte tests are created: one for the API, and one for the database connection. Just head to movie_api/test and run `pytest`.