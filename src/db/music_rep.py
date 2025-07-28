from typing import Dict, List, Optional, Any
from .track_rep import ArtistRepository, AlbumRepository, TrackRepository

class MusicRepository:
    def __init__(self, db_path: str):
        self.artist_repo = ArtistRepository(db_path)
        self.album_repo = AlbumRepository(db_path)
        self.track_repo = TrackRepository(db_path)

    def new_album_tracklist(self, album_data: Dict[str, Any]) -> str:
        """Create a new album in the database"""

        album_id = self.album_repo.new_album(album_data)
        
        if not album_id:
            raise ValueError("Failed to create new album")

        print(f"Album '{album_data.title}' by {album_data.album_artist} (ID: {album_id}) initialized.")
        self.track_repo.new_tracklist(album_data.tracklist, album_id)
        print(f"Tracks initialized")
        return album_id
