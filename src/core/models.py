from dataclasses import dataclass

# Data Models / Schemas

# TODO(OPTIONAL): add dictionary conversion
# no flags, only data
@dataclass
class TrackData:
    title: str = ''
    path: str = ''
    duration_ms: float = 0
    fingerprint: str = ''
    track_number: int = 0
    disc_number: int = 0
    format: str = ''

@dataclass
class AlbumData:
    title: str = ''
    release_year: str = ''
    album_artist: str = ''
    total_tracks: int = 0
    path: str = ''
    tracklist: list[TrackData] = None



# ###  Business Logic / Domain Services
# def is_subgenre(child: str, parent: str) -> bool:
#     """Check if child is a subgenre of parent"""
#     pass


# ###  Value Objects / Enums
# # core/constants.py
# class MetadataStatus(str, Enum):
#     PENDING = 'pending'
#     COMPLETE = 'complete'