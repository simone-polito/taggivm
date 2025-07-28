import os
from dotenv import load_dotenv
from pathlib import Path

# global variables
DEFAULT_MUSIC_DIR = Path.home() / "music"
DEFAULT_DB_PATH = Path.home() / ".local" / "share" / "taggivm" / "music.db" # linux
DEFAULT_DB_PATH = Path.home() / "Library" / "Application Support" / "taggivm" / "music.db" # mac

# load .env file
load_dotenv()

# access environment variables (forced absolute)
MUSIC_LIBRARY_PATH = Path(os.getenv("MUSIC_LIBRARY_PATH", DEFAULT_MUSIC_DIR)).expanduser().resolve()
DB_PATH = Path(os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)).expanduser().resolve()
# DEBUG = os.getenv("DEBUG", "false").lower() == "true"
