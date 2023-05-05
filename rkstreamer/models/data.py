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

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class SongSearch(SongBase):
    """Song Search model'"""
    token: str = None


@dataclass
class SongQueue():
    """Song Queue model"""
    songs: field(default_factory=list)


@dataclass
class PlaylistBase():
    """Playlist base model"""
    name: str


@dataclass
class Playlist(PlaylistBase):
    """Playlist model"""
    songs: field(default_factory=list)


@dataclass
class PlaylistSearch(PlaylistBase):
    """Playlist search model"""
    count: int = None
    token: str = None


@dataclass
class Album():
    """Album model"""
    name: str
    songs: field(default_factory=list)
