from pathlib import Path
import json
import pyaudio
from .logger import log
from dotenv import load_dotenv
import os



log.info("Config initialized.")
def load_config():
    """Loads the settings from the settings.json-file."""
    config_path = Path(__file__).parent.parent / "settings" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


CONFIG = load_config()
SERVER_ADDRESS = CONFIG["SERVER_ADDRESS"]
PORT = CONFIG["SERVER_PORT"]
PASSWORD = CONFIG["PASSWORD"]
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")

# Audio Konstanten
CHUNK_SIZE = 1024
CHANNELS = 1
RATE = 16000
FORMAT = pyaudio.paInt16
SILENCE_THRESHOLD = 250
SILENCE_DURATION = 2  # Sekunden