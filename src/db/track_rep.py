from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from core import TrackData, AlbumData
from .base_rep import BaseRepository

class ArtistRepository(BaseRepository):
    def __init__(self, db_path: str):
        super().__init__(db_path)







class AlbumRepository(BaseRepository):
    def __init__(self, db_path: str):
        super().__init__(db_path)


    def new_album(self, album: AlbumData) -> int:
        """
        Insert a new, firstly scanned, album into the database.
        Returns the ID of the newly created album.
        
        Args:
            album: Album dataclass instance
            
        Returns:
            int: ID of the newly created album
        """
        # TODO: add checks if it already exist even if it sholdn't thanks to .scanned
        
        album_data = {
            'artist_id': 0, # placeholder, will be set later
            'title': album.title,
            'release_year': album.release_year,
            'album_artist': album.album_artist,
            'total_tracks': album.total_tracks,
            'path': album.path,
            'metadata_status': 'pending',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # .isoformat()
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        album_id = self._insert('albums', album_data)
        return album_id





class TrackRepository(BaseRepository):
    def __init__(self, db_path: str):
        super().__init__(db_path)


    def new_tracklist(self, track_list: List[TrackData], album_id: int) -> List[int]:
        """
        Insert new, firstly scanned, tracks into the database.
        Returns the ID of the newly created track.

        Args:
            track_list: List of track dataclass instance

        Returns:
            int: ID of the newly created track
        """
        if not track_list:
            raise ValueError("Track list cannot be empty")
        
        track_data_list = []
        for track in track_list:
            
            track_data = {
                'album_id': album_id,
                'title': track.title,
                'path': track.path,
                'duration_ms': track.duration_ms,
                'fingerprint': track.fingerprint,
                'track_number': track.track_number,
                'disc_number': track.disc_number,
                'format': track.format,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            track_data_list.append(track_data)

        track_id = self._insert_many('tracks', track_data_list)
        return track_id
