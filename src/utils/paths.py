"""
Centralized path management for the project.
"""
from pathlib import Path

# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Standard Directories
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "configs"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Specific Data Paths
RAW_DATA_PATH = DATA_DIR / "raw_dataset.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed_dataset.csv"

# Ensure directories exist
def ensure_directories():
    for directory in [DATA_DIR, MODELS_DIR, OUTPUTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

ensure_directories()
