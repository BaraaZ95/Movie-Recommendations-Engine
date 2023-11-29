# import logging
from cosine_pipeline import prepare_data

# from data.wandb_log import load_and_log
from postgres import create_sim_matrix_table, send_csv_to_psql

# _logger = logging.getLogger(__name__)


def main():
    prepare_data()
    # Uploading the movies to postgres is easy, however, for the sim matrix, a separate pipeline is needed
    # load_and_log() # If you wish to log the movies datasets to wandb

    # Create the sim matrix table in postgres
    create_sim_matrix_table()
    # Copy the sim matrix to postgres
    send_csv_to_psql("movie_model/data/clean/sim_matrix.csv", "sim_matrix")


prepare_data()
if __name__ == "main":
    main()
