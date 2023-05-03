"""
DI Module for stream providers API
"""

from __future__ import annotations
from typing import Union, TYPE_CHECKING
from ._interface import ABC,abstractmethod

if TYPE_CHECKING:
    from rkstreamer.types import (
        SongListRawType,
        SongUrl)

class ISongProvider(ABC):
    """Interface for song provider"""

    @abstractmethod
    def search_songs(self, search_string: str) -> SongListRawType:
        """Search songs"""

    @abstractmethod
    def select_song(self, arg: Union[int,str]) -> SongUrl:
        """Select song"""


class IAlbumProvider(ABC):
    """Interface for album provider"""

    @abstractmethod
    def search_albums(self, search_string: str):
        """Search albums"""

    @abstractmethod
    def select_album(self, arg: int):
        """Select song"""

    @abstractmethod
    def select_song_from_album(self, arg: int):
        """Select song"""


class IPlaylistProvider(ABC):
    """Interface for playlist provider"""

    @abstractmethod
    def search_playlists(self, search_string: str):
        """Search albums"""

    @abstractmethod
    def select_playlist(self, arg: int):
        """Select song"""
