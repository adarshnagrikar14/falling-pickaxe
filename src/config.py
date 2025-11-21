import json
import os
import shutil
from pathlib import Path

# Determine the base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_CONFIG_PATH = BASE_DIR / "default.config.json"

# If config.json does not exist, copy from default.config.json
if not CONFIG_PATH.exists() and DEFAULT_CONFIG_PATH.exists():
    try:
        shutil.copy(DEFAULT_CONFIG_PATH, CONFIG_PATH)
    except PermissionError:
        print("Warning: Could not copy default config to config.json due to permissions. Using default config directly.")
        CONFIG_PATH = DEFAULT_CONFIG_PATH

if not CONFIG_PATH.exists():
    # Fallback to check if we are in a structure where config is in the same dir (e.g. flattened build)
    if (Path(__file__).parent / "config.json").exists():
        CONFIG_PATH = Path(__file__).parent / "config.json"
    else:
        raise FileNotFoundError(f"Configuration file 'config.json' not found at {CONFIG_PATH}. Please create it or copy from 'default.config.json'.")

# Load configuration
with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)
