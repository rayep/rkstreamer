"""Type used by Controllers"""

from typing import NewType
from rkstreamer.interfaces import ISongController

SongControllerType = NewType('ISongController', ISongController)
