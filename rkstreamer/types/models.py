"""
Types used by domain models
"""

from typing import NewType
from rkstreamer.models.data import (
    Song,
    SongSearch,
    SongQueue)
from rkstreamer.interfaces import (
    ISongModel,
    ISongQueue,
    IAlbumModel,
    IAlbumQueue,
    ISongProvider)

# Interfaces

SongModelType = NewType('ISongModel', ISongModel)
SongQueueModelType = NewType('ISongQueue', ISongQueue)
AlbumModelType = NewType('IAlbumModel', IAlbumModel)
AlbumQueueModelType = NewType('IAlbumQueue', IAlbumQueue)

# Primitives

SongRawType = NewType('SongRaw', dict[str,str])
SongListRawType = NewType('SongListRaw', list[dict[str,str]])

# Data

SongType = NewType('Song', Song)
SongListType = NewType('SongList', list[Song])
SongIndexType = NewType('SongIndex', dict[int, Song])
SongUrl = NewType('SongUrl', str)
SongSearchType = NewType('SongSearch', SongSearch)
SongSearchIndexType = NewType('SongSearchIndex', dict[int,SongSearch])
SongQueueType = NewType('SongQueue', SongQueue)
SongQueueIndexType = NewType('SongQueueIndex', dict[int,SongQueue])

SongProviderType = NewType("SongProvider", ISongProvider)
