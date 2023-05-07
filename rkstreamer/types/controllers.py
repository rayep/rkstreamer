"""Type used by Controllers"""

from typing import NewType
from rkstreamer.interfaces import ISongController, IAlbumController

SongControllerType = NewType('ISongController', ISongController)
AlbumControllerType = NewType('IAlbumController', IAlbumController)
