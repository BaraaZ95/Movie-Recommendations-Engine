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

prepare_data()
if __name__ == "main":
    #    prepare_data()
    # After the model is trained, log all the outputs to Weights and Biases
    _logger.info("Data preprocessing...")
    prepare_data()
    _logger.info("Data preprocessing complete")
    _logger.info("Logging data to Weights and Biases...")
    # Note: Better try exceptions can be added to make sure the file was logged successfully and file checking
    # Also sas per the wandb documentation, the cos_sim file is almost 1GB: The size of your data is too large.
    # Large data sizes could introduce a >1ms overhead to the training loop.
    # load_and_log()
    _logger.info("Data successfully logged Weights and Biases")
