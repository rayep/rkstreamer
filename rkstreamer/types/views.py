"""Types used by Views"""

from typing import NewType
from rkstreamer.interfaces import ISongView, IAlbumView

SongViewType = NewType('ISongView', ISongView)
AlbumViewType = NewType('IAlbumView', IAlbumView)

