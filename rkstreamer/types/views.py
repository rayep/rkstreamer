"""Types used by Views"""

from typing import NewType
from rkstreamer.interfaces import ISongView

SongViewType = NewType('ISongView', ISongView)
