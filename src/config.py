import os
from dotenv import load_dotenv
from pathlib import Path

# global variables
DEFAULT_MUSIC_DIR = Path.home() / "music"
# DEFAULT_DB_PATH = Path("music.db")

# load .env file
load_dotenv()

# access environment variables
MUSIC_LIBRARY_PATH = os.getenv("MUSIC_LIBRARY_PATH", DEFAULT_MUSIC_DIR)
# DATABASE_PATH = Path(os.getenv("DATABASE_PATH", DEFAULT_DB_PATH))
# DEBUG = os.getenv("DEBUG", "false").lower() == "true"
