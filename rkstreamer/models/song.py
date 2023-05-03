"""
Models - Song
"""

from typing import Optional
from rkstreamer.types import (
    SongListRawType,
    SongType,
    SongSearchType,
    SongSearchIndexType,
    SongQueueType,
    SongQueueIndexType,
    SongQueueModelType,
    NetworkProviderType)
from rkstreamer.interfaces.models import ISongModel, ISongQueue
from rkstreamer.services.provider import JioSaavnSongProvider
from rkstreamer.models.data import Song, SongSearch, SongQueue
from rkstreamer.models.exceptions import (
    AddMediaError,
    RemoveMediaError,
    GetMediaError,
    MediaNotFound,
    InvalidInput
)

class JioSaavnSongModel(ISongModel):
    """Song model implemented for Jio Saavn Service"""

    def __init__(self, network_provider: NetworkProviderType) -> None:
        self.stream_provider = JioSaavnSongProvider(client=network_provider)
        self.queue: SongQueueModelType = JioSaavnSongQueue()
        self.indexed_search_songs: SongSearchIndexType = {}
        self._search_songs = []

    def _create_song(self, **kwargs) -> SongType:
        return Song(**kwargs)

    def _create_recomm_song(self, args) -> SongType:
        return Song(**args)

    def _create_search_song(self, **kwargs) -> SongSearchType:
        return SongSearch(**kwargs)

    def _create_search_song_index(self, songs: SongListRawType) -> SongSearchIndexType:
        for count, song in enumerate(songs, 1):
            self.indexed_search_songs.update(
                {count: self._create_search_song(**song)})
        return self.indexed_search_songs

    def search_songs(self, search_string: str) -> SongSearchIndexType:
        search_result: SongListRawType = self.stream_provider.search_songs(
            search_string)
        return self._create_search_song_index(search_result)

    def select_song(self, song_number: int) -> Optional[SongType]:
        selected_song = self.indexed_search_songs.get(int(song_number))
        if selected_song:
            song_url = self.stream_provider.select_song(selected_song.token)
            if song_url:
                selected_song.__dict__.update({'stream_url': song_url})
                selected_song.__dict__.update({'status': 'Loaded'})
                return self._create_song(**selected_song.__dict__)
        raise InvalidInput("Invalid song selection input provided.")

    def select_song_using_eurl(self, enc_url: str) -> str:
        """Get the song stream url using Enc Url Token"""
        stream_url = self.stream_provider.select_song(enc_url)
        return stream_url

    def get_rsongs(self, song_id: str) -> list[SongType]:
        """Gets recommended songs from song_id"""
        recomm_songs_raw: SongListRawType = self.stream_provider.get_recomm_songs(song_id)
        rsongs_list = list(map(self._create_recomm_song, recomm_songs_raw))
        self.queue.rsongs_copy_.append(rsongs_list) # making a copy of all rsongs to avoid dups.
        return rsongs_list


class JioSaavnSongQueue(ISongQueue):
    """Song queue implemented for Jio Saavn"""

    def __init__(self) -> None:
        self.queue: SongQueueType = SongQueue([])
        self._indexed_queue = {}
        self.rsongs_copy_ = []
        self.rsongs_list: list[SongType] = []

    def add_song(self, song: SongType) -> bool:
        if not self._check_media(song):
            self.queue.songs.append(song)
            self._normalize_queue_index()
            print(f"\n\033[01m\033[32mAdded: '{song.name}' to queue!\033[0m")
        if not self._check_media(song):
            raise AddMediaError("Failed to add media to queue")
        if song not in self._indexed_queue.values():
            raise AddMediaError("Failed to add media to queue index")
        return True

    def add_recomm_song(self, songs: SongListRawType) -> None:
        """Add recommended songs to queue index"""
        queue_length = len(self.queue.songs)
        for song in songs:
            if not self._check_media(song):
                self.queue.songs.append(song)
        for count, song in enumerate(self.queue.songs, queue_length+1):
            self._indexed_queue.update({count:song})

    def _check_media(self, song: SongType) -> bool:
        """Checks the presence of media"""
        if song in self.queue.songs:
            return True
        return False

    def _normalize_queue_index(self) -> None:
        """Updates the queue with index"""
        for count, song in enumerate(self.queue.songs,1):
            self._indexed_queue.update(
                {count: song})

    def remove_song(self, index: int) -> list[SongType]:
        removed_songs = []
        for ind in list(index):
            song = self.fetch_song(int(int(ind)))
            if self._check_media(song):
                self.queue.songs.remove(song)
                self._indexed_queue.pop(int(ind))
                removed_songs.append(song)
                print(f"\n\033[93mRemoved: '{song.name}' from main queue!\033[0m")
            else:
                raise MediaNotFound("Media not found in queue to delete")
            if song in self._indexed_queue.values():
                raise RemoveMediaError("Failed to remove media from queue index")
        self._normalize_queue_index()
        return removed_songs

    def fetch_song(self, index: int) -> SongType:
        song = self._indexed_queue.get(int(index))
        if not song:
            raise GetMediaError("Failed to get media from queue index")
        return song

    def update_status(self, status: str, stream_url: str) -> None:
        """Update 'played' status for songs in main queue"""
        for song in self.queue.songs:
            if (stream_url == song.stream_url) and (song.status == 'Loaded'):
                print(f"\n\033[31m>>> Playing '{song.name}' <<<\033[0m\n ")
                song.status = status
                return song
        return None

    @property
    def get_queue(self) -> SongQueueType:
        return self.queue

    @property
    def get_indexed_queue(self) -> SongQueueIndexType :
        """returns the indexed queue"""
        return self._indexed_queue

    def check_status(self, queue: SongQueueType):
        """Checks the queue status for 'played' songs"""
        for song in queue.songs:
            if song.status == 'Played':
                continue
            else:
                return False
        return True

    def get_rsong(self):
        """Pop rsong from its queue and move it to main queue.
        Change the song status to 'Loaded'"""
        if self.rsongs_list:
            rsong = self.rsongs_list.pop(0)
            rsong.status = 'Loaded'
            return rsong
        return None

    def get_rsong_index(self, index: int) -> Optional[SongType]:
        """Get RS song from the given index"""
        try:
            rsong = self.rsongs_list.pop(index)
            return rsong
        except IndexError:
            print("Invalid RS Index!")
        return None

    def remove_rsong_index(self, index: int) -> None:
        """Removes the RS song from its queue"""
        try:
            rsong = self.rsongs_list.pop(index)
            if rsong:
                print(f"\n\033[33mRemoved: '{rsong.name}' from RS queue!\033[0m")
        except IndexError:
            print("Invalid RS Index!")

    @property
    def get_rsongs(self):
        """Get the rsongs list"""
        return self.rsongs_list

    def update_rqueue(self, rsongs: list[SongType]):
        """Update the rsongs list"""
        for song in rsongs:
            if song not in self.rsongs_copy_:
                self.rsongs_list.append(song)
