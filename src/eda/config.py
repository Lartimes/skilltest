from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "output" / "cleaned"

# EDA output directory
OUTPUT_DIR = PROJECT_ROOT / "output" / "eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Image save directory
IMG_SAVE_DIR = OUTPUT_DIR / "images"
IMG_SAVE_DIR.mkdir(parents=True, exist_ok=True)
