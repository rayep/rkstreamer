"""
DI module for domain models
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from ._interface import ABC, abstractmethod

if TYPE_CHECKING:
    from rkstreamer.types import (
        SongSearchIndexType,
        SongType,
        SongQueueType,
        SongQueueIndexType)


class ISongModel(ABC):
    """Interface for Song"""

    @abstractmethod
    def search_songs(self, search_string: str) -> SongSearchIndexType:
        """Search songs"""

    @abstractmethod
    def select_song(self, song_number: int) -> Optional[SongType]:
        """Select song"""


class ISongQueue(ABC):
    """Interface for song queue"""

    @abstractmethod
    def add_song(self, song: SongType) -> bool:
        """Add song to queue"""

    @abstractmethod
    def remove_song(self, index: int) -> list(SongType):
        """Remove song from queue and updates the index"""

    @abstractmethod
    def fetch_song(self, index: int) -> SongType:
        """fetch song from queue index"""

    @property
    @abstractmethod
    def get_queue(self) -> SongQueueType:
        """Returns the song queue"""

    @property
    @abstractmethod
    def get_indexed_queue(self) -> SongQueueIndexType:
        """Returns the indexed song queue"""
