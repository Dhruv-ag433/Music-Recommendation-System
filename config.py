from pathlib import Path
import os

# Project root (where app.py exists)
BASE_DIR = Path(__file__).resolve().parent

# Default data directory inside project
DEFAULT_DATA_DIR = BASE_DIR / "dataset"

# Allow override via environment variable
DATA_DIR = Path(os.getenv("DATA_DIR", DEFAULT_DATA_DIR)).resolve()

# Create directory if it doesn't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATASET_FILE = DATA_DIR / "spotify_tracks_with_audio_features.csv"
FEATURES_FILE = DATA_DIR / "features.parquet"