from pathlib import Path
import strictyaml
from pydantic import BaseModel
import sys
from pathlib import Path  # if you haven't already done so

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
print(root)
sys.path.append(str(root))
from movie_model import ml_model

# Project directories
PACKAGE_ROOT = Path(ml_model.__file__).resolve().parent
print(PACKAGE_ROOT)
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"
DATASET_DIR = PACKAGE_ROOT / "data"
RAW_DATA_DIR = DATASET_DIR / "raw"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "models"


class AppConfig(BaseModel):
    """
    Application level configuration.
    """

    package_name: str
    pipeline_name: str
    pipeline_save_file: str
    data: str


class ModelConfig(BaseModel):
    """
    All configuration relevant to model
    training and feature engineering
    """

    original_title: str
    popularity: str
    weighted_average: str
    score: str
    bag_of_words: str


class Config(BaseModel):
    """Master config object"""

    app_config: AppConfig
    model_config: ModelConfig


def find_config_file():
    """Locate the configuration file"""
    if CONFIG_FILE_PATH.is_file():
        print(CONFIG_FILE_PATH)
        return CONFIG_FILE_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH}")


def fetch_config_from_yaml(cfg_path=None):
    "Parse YAML containing the package configuration."

    if not cfg_path:
        cfg_path = find_config_file()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = strictyaml.load(conf_file.read())
            return parsed_config
    raise OSError(f"Did not find confige file at path: {cfg_path}")


def create_and_validate_config(parsed_config=None):
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()

    # specify the data attribute from the strictyaml YAML type.
    _config = Config(
        app_config=AppConfig(**parsed_config.data),  # type: ignore
        model_config=ModelConfig(**parsed_config.data),  # type: ignore
    )
    return _config


config = create_and_validate_config()
