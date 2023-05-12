"""Models - Album"""

from rkstreamer.interfaces.models import IAlbumModel
from rkstreamer.models.song import JioSaavnSongQueue
from rkstreamer.models.data import Album, AlbumSearch, Song
from rkstreamer.services.album import JioSaavnAlbumProvider
from rkstreamer.services.song import JioSaavnSongProvider
from rkstreamer.types import (
    NetworkProviderType,
    SongQueueModelType,
    SongType,
    SongListRawType
)
from rkstreamer.models.exceptions import (
    InvalidInput
)

class JioSaavnAlbumModel(IAlbumModel):
    """Album model implemented for Jio Saavn service"""

    def __init__(self, network_provider: NetworkProviderType) -> None:
        self.network_provider = network_provider
        self.stream_provider = JioSaavnAlbumProvider(client=self.network_provider)
        self.song_provider = JioSaavnSongProvider(client=self.network_provider)
        self.queue: SongQueueModelType = JioSaavnSongQueue()
        self.indexed_search_albums = {}
        self.indexed_album_songs = {}

    def _create_album_song(self, **kwargs):
        return Song(**kwargs)

    def _create_search_album(self, **kwargs):
        return AlbumSearch(**kwargs)

    def _create_album(self, **kwargs):
        return Album(**kwargs)

    def _create_search_album_index(self, albums):
        self.indexed_search_albums.clear()
        for count, album in enumerate(albums, 1):
            self.indexed_search_albums.update(
                {count: self._create_search_album(**album)})
        return self.indexed_search_albums

    def _create_album_song_index(self, albums):
        self.indexed_album_songs.clear()
        for count, album in enumerate(albums, 1):
            self.indexed_album_songs.update(
                {count: self._create_album_song(**album)})
        return self.indexed_album_songs

    def _create_recomm_song(self, args) -> SongType:
        return Song(**args)

    def search(self, search_string: str, **kwargs):
        search_result = self.stream_provider.search_albums(search_string, **kwargs)
        return self._create_search_album_index(search_result)

    def select(self, selection: int, **kwargs):
        selected_album = self.indexed_search_albums.get(int(selection))
        if selected_album:
            album_songs_raw = self.stream_provider.select_album(selected_album.id)
            selected_album.__dict__.update(
                {'songs': self._create_album_song_index(album_songs_raw)})
            return self._create_album(**selected_album.__dict__)
        raise InvalidInput("Invalid album selection input provided.")

    def select_album_using_id(self, album_id: str):
        """Select album using ID"""
        album_songs_raw = self.stream_provider.select_album_id(album_id)
        album_songs_raw.update(
            {'songs': self._create_album_song_index(album_songs_raw['songs'])})
        return self._create_album(**album_songs_raw)

    def select_song_from_album(self, selection: int):
        """Selecting song from the album"""
        selected_song = self.indexed_album_songs.get(selection)
        if selected_song:
            song_url = self.song_provider.select_song(selected_song.token)
            if song_url:
                selected_song.__dict__.update({'stream_url': song_url})
                selected_song.__dict__.update({'status': 'Loaded'})
                return selected_song
        raise InvalidInput("Invalid album song selection input provided.")

    def get_related_songs(self, data: str) -> list[SongType]:
        """Gets recommended songs using song_id and updates the RQueue"""
        recomm_songs_raw: SongListRawType = self.song_provider.get_recomm_songs(data)
        if recomm_songs_raw:
            return list(map(self._create_recomm_song, recomm_songs_raw))
        return None

    def get_song_url(self, data: str) -> str:
        """Get the song's stream url using Enc Url Token - used for rsongs download"""
        stream_url = self.song_provider.select_song(data)
        return stream_url
