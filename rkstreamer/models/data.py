"""Data Models"""

from ._model import dataclass, field

@dataclass
class SongBase():
    """Base for song model"""
    name: str
    id: str = None
    artists: str = None
    music: str = None
    album_name: str = None
    album_id: str = None
    duration: int = None
    status: str = None


@dataclass
class Song(SongBase):
    """Song model"""
    token: str = None
    stream_url: str = None


@dataclass
class SongSearch(SongBase):
    """Song Search model'"""
    token: str = None

@dataclass
class SongQueue():
    """Song Queue model"""
    songs: field(default_factory=list)


@dataclass
class Playlist():
    """Playlist model"""
    name: str
    songs: field(default_factory=list)


@dataclass
class Album():
    """Album model"""
    name: str
    songs: field(default_factory=list)
