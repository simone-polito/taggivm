import os
import re
from pathlib import Path

# regex for album folder name like "1999 - OK Computer"
ALBUM_NAME_PATTERN = re.compile(r"^\d{4} - .+")

# supported audio file extensions
AUDIO_EXTS = ('.mp3', '.flac', '.wav', '.m4a')
def discover_scan(src_filepath: Path ) -> list:
    """
    Discover scan files in the current directory.

    Returns:
        list: A list of scan file paths.
    """

    to_scan_albums = []
    to_skip_albums = []
    src_filepath = src_filepath.resolve()  # force absolute path

    for root, dirs, files in os.walk(src_filepath):
        root_path = Path(root)

        if '.scanned' in files:
            to_skip_albums.append(root_path)
            continue

        if not any(f.lower().endswith(AUDIO_EXTS) for f in files):
            continue

        rel_parts = root_path.relative_to(src_filepath).parts

        if len(rel_parts) != 2:
            print(f"⚠️ Invalid folder structure: '{root_path}' should be two levels deep (e.g., 'Artist/Album').")
            to_skip_albums.append(root_path)
            continue

        album_folder = rel_parts[1]
        if not ALBUM_NAME_PATTERN.match(album_folder):
            print(f"⚠️  Naming issue: '{album_folder}' does not match 'YYYY - Album Title'")
            to_skip_albums.append(root_path)
            continue

        to_scan_albums.append(root_path)
        
    return to_scan_albums, to_skip_albums


def init_album_DB(album_paths: list[Path]) -> None:
    """
    Initialize database new albums with discovered scan files.

    Args:
        album_paths (list): List of album paths to initialize.
    """
    for album in album_paths:
       print(f"Initializing database for album: {album}")

