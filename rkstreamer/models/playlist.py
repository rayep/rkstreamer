"""Models - Playlist"""

from rkstreamer.models.data import Playlist, PlaylistSearch, Song
from rkstreamer.models.song import JioSaavnSongQueue
from rkstreamer.interfaces.models import IPlaylistModel
from rkstreamer.services.playlist import JioSaavnPlaylistProvider
from rkstreamer.types import (
    NetworkProviderType
)
from rkstreamer.models.exceptions import InvalidInput


class JioSaavnPlaylistModel(IPlaylistModel):
    """Playlist model implemented for Jio Saavn service"""

    def __init__(self, network_provider: NetworkProviderType) -> None:
        self.stream_provider = JioSaavnPlaylistProvider(
            client=network_provider)
        self.queue = JioSaavnSongQueue()
        self.indexed_playlists = {}
        self.playlist_songs = []

    def _create_playlist(self, **kwargs):
        return Playlist(**kwargs)

    def _create_search_playlist(self, **kwargs):
        return PlaylistSearch(**kwargs)

    def _create_search_playlist_index(self, playlists):
        for count, playlist in enumerate(playlists, 1):
            self.indexed_playlists.update(
                {count: self._create_search_playlist(**playlist)})
        return self.indexed_playlists

    def search(self, search_string: str, **kwargs):
        response = self.stream_provider.search_playlists(
            search_string, **kwargs)
        return self._create_search_playlist_index(response)

    def select(self, selection: int, **kwargs):
        selected_plist = self.indexed_playlists.get(int(selection))
        if selected_plist:
            plist_songs = self.stream_provider.select_playlist(
                selected_plist.token, **kwargs)
            if plist_songs:
                selected_plist.__dict__.update(
                    {'songs': [Song(**song, status='Loaded') for song in plist_songs]})
                return self._create_playlist(**selected_plist.__dict__)
        raise InvalidInput("Invalid playlist selection input provided.")
