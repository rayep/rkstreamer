"""
DI module for Views
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from ._interface import ABC, abstractmethod

if TYPE_CHECKING:
    from rkstreamer.types import (
        SongSearchIndexType,
        SongType,
        SongQueueIndexType
    )


class ISongView(ABC):
    """Interface for Song View"""

    @abstractmethod
    def display_songs(self, songs: SongSearchIndexType) -> None:
        """Displays the songs search result"""

    @abstractmethod
    def display_selected_song(self, song: SongType) -> None:
        """Displays the songs search result"""

    @abstractmethod
    def display_queue(self, queue: SongQueueIndexType) -> None:
        """Displays the songs queue"""

    @abstractmethod
    def play_media(self, song: SongType) -> None:
        """Play the given media"""

