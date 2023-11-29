import psycopg2
from sqlalchemy import create_engine, VARCHAR, FLOAT, TEXT, INTEGER

import pandas as pd

PG_USER = "postgres"
PG_PASSWORD = "pass"
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "test"
TABLE_NAME = "movies"


# First let's write the movies dataframe to postgres
def upload_to_postgres(df: pd.DataFrame, TABLE_NAME: str) -> None:
    df_postgres = (
        df.reset_index()
        .rename(columns={"index": "movie_index"})
        .set_index("movie_index")
    )
    # Establish a connection
    engine = create_engine(
        f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    )
    dtype = {
        "original_title": VARCHAR(255),
        "popularity": FLOAT,
        "weighted_average": FLOAT,
        "score": FLOAT,
        "bag_of_words": TEXT,
        "movie_index": INTEGER,
    }

    df_postgres.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",  # Replace only used for testing purposes
        index=True,
        dtype=dtype,
        index_label="movie_index",
    )

    # Test to make sure the databases are the same:
    # retrieved_df = pd.read_sql("SELECT * FROM movies;",engine)
    #
    # local_dataframe = df_postgres.sort_values(by=df.columns.tolist()).reset_index(drop=True)
    # postgres_dataframe = retrieved_df.reset_index(drop=True).sort_values(
    #    by=retrieved_df.columns.tolist()
    # )
    #
    # comparison_result = local_dataframe.compare(postgres_dataframe)
    # Or use assert
    # assert local_dataframe == postgres_dataframe
    # print("Differences:")
    # print(comparison_result)


def create_sim_matrix_table():
    conn = psycopg2.connect(
        host=PG_HOST, database=PG_DATABASE, user=PG_USER, password=PG_PASSWORD
    )
    cur = conn.cursor()

    # Define the table structure
    # DROP TABLE only used for testing purposes
    create_table_sql = """
    DROP TABLE IF EXISTS sim_matrix;
    CREATE TABLE sim_matrix (
        movie_id_a INT,
        movie_id_b INT,
        similarity_score FLOAT
    );
    """

    # Execute the CREATE TABLE command
    cur.execute(create_table_sql)
    conn.commit()
    cur.close()
    conn.close()


def send_csv_to_psql(csv, table_):
    conn = psycopg2.connect(
        host=PG_HOST, database=PG_DATABASE, user=PG_USER, password=PG_PASSWORD
    )
    # Copying a csv to postgres is much faster than writing the dataframe to postgres
    sql = "COPY %s FROM STDIN WITH CSV HEADER DELIMITER AS ','"
    file = open(csv, "r")
    table = table_
    with conn.cursor() as cur:
        cur.execute("truncate " + table + ";")  # avoiding uploading duplicate data!
        cur.copy_expert(sql=sql % table, file=file)  # type: ignore
        conn.commit()
    #         cur.close()
    #         conn.close()
    return conn.commit()
