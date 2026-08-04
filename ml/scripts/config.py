"""Paths and shared settings for the offline ML pipeline."""

from pathlib import Path

ML_DIRECTORY = Path(__file__).resolve().parents[1]
DATASET_DIRECTORY = ML_DIRECTORY / "dataset"
TRAIN_DIRECTORY = DATASET_DIRECTORY / "train"
TEST_DIRECTORY = DATASET_DIRECTORY / "test"
MODELS_DIRECTORY = ML_DIRECTORY / "models"

BEST_MODEL_PATH = MODELS_DIRECTORY / "best_model.pkl"
TFIDF_VECTORIZER_PATH = MODELS_DIRECTORY / "tfidf_vectorizer.pkl"
LABEL_ENCODER_PATH = MODELS_DIRECTORY / "label_encoder.pkl"

RANDOM_STATE = 42
VALIDATION_SIZE = 0.2
TEST_SIZE = 0.2
MAX_FEATURES = 30_000
