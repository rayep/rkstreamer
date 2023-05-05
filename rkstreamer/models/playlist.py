"""Models - Playlist"""

from rkstreamer.models.data import Playlist, PlaylistSearch
from rkstreamer.interfaces.models import IPlaylistModel, IPlaylistQueue
from rkstreamer.services.provider import JioSaavnPlaylistProvider
from rkstreamer.types import (
    NetworkProviderType
)

class JioSaavnPlaylistModel(IPlaylistModel):
    """Playlist model implemented for Jio Saavn service"""

    def __init__(self, network_provider: NetworkProviderType) -> None:
        self.stream_provider = JioSaavnPlaylistProvider(client=network_provider)
