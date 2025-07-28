import os
import re
from pathlib import Path
from typing import Dict, List
from core import TrackData, AlbumData
from db import MusicRepository

# regex for album folder name like "1999 - OK Computer"
ALBUM_NAME_PATTERN = re.compile(r"^\d{4} - .+")

# supported audio file extensions
AUDIO_EXTS = ('.mp3', '.flac', '.wav', '.m4a')
def discover_scan(src_filepath: Path ) -> Dict[str, Dict[str, Path]]:
    """
    Discover scan files in the current directory.

    Returns:
        dict: A dictionary mapping artist names to their album paths.
    """

    to_scan_albums = []
    to_skip_albums = []
    src_filepath = src_filepath.resolve()  # force absolute path

    scan_tree = {}
    
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

        artist_folder = rel_parts[0]

        if artist_folder not in scan_tree:
            scan_tree[artist_folder] = {}
        scan_tree[artist_folder][album_folder] = root_path

    return scan_tree

    

def init_album_DB(scan_tree:  Dict[str, Dict[str, Path]], db_path: Path) -> None:
    """
    Insert initial data for newly discovered artists, albums, and tracks into the database.

    Args:
        scan_tree (dict): Nested dict of artist -> album -> path.
    """
    for artist, albums in scan_tree.items():
        for album, album_path in albums.items():
            year, album_title = album.split(' - ', 1)
            for root, dirs, files in os.walk(album_path):
                
                total_tracks = sum(1 for f in files if f.lower().endswith(AUDIO_EXTS))
                album_obj = AlbumData(
                    title=album_title,
                    release_year=year,
                    album_artist=artist,
                    total_tracks=total_tracks,
                    path=album_path.as_posix(),
                    tracklist=[]
                )
                
                for f in files:
                    if f.lower().endswith(AUDIO_EXTS):
                        title, format = f.rsplit('.', 1)
                        # check why with e.. di yeat seams spaced
                        track_obj = TrackData(
                            title=title,
                            path=(Path(root) / f).as_posix(),
                            format=format,
                        )
                        album_obj.tracklist.append(track_obj)
                
            # Initialize the album in the database
            music_repo = MusicRepository(db_path)
            album_id = music_repo.new_album_tracklist(album_obj)

            # touch .scanned file to mark as scanned
            # (album_path / '.scanned').touch()


            ## IMPROVEMENT: musicobject function that handdles album and artist id, make no sense to have it on the data structure