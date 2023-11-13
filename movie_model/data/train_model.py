import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import logging
from data.cosine_pipeline import prepare_data, COS_SIM_NAME
import pickle
from data.wandb_log import load_and_log

# from skops.io import dump
_logger = logging.getLogger(__name__)


def train_model():
    cos_sim = prepare_data()
    # SIM_MATRIX_NAME = 'cosine_similarity.skops' # If using skops
    _logger.info(f"Saving the cosine similarity matrix as {COS_SIM_NAME}")
    # Save the similarity matrix using skops
    # serialized = dump(cos_sim, SIM_MATRIX_NAME)
    # Save using pickle
    pickle.dump(cos_sim, open(COS_SIM_NAME, "wb"))
    # or dump(cos_sim, "COS_SIM_NAME.skops")
    _logger.info("Data preprocessing complete...")


if __name__ == "main":
    train_model()
    # After the model is trained, log all the outputs to Weights and Biases
    load_and_log()
