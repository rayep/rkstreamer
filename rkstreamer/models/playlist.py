"""Models - Playlist"""

from ._model import dataclass, field

@dataclass
class Playlist():
    """Playlist model"""
    name: str
    songs: field(default_factory=list)
