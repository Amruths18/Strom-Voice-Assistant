# File: src/config.py
import os

# Get the project root directory automatically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
MODEL_PATH = os.path.join(BASE_DIR, "assets", "models", "vosk-model-small-en-us-0.15")
DB_PATH = os.path.join(BASE_DIR, "data", "assistant_data.db")

# Voice Settings
VOICE_RATE = 150
WAKE_WORD = "assistant"