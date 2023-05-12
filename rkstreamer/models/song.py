"""
Models - Song
"""

from typing import Optional
from rkstreamer.models.data import Song, SongSearch, SongQueue
from rkstreamer.interfaces.models import ISongModel, ISongQueue
from rkstreamer.services.song import JioSaavnSongProvider
from rkstreamer.types import (
    SongListRawType,
    SongType,
    SongSearchType,
    SongSearchIndexType,
    SongQueueType,
    SongQueueIndexType,
    SongQueueModelType,
    NetworkProviderType)
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
        self.network_provider = network_provider
        self.stream_provider = JioSaavnSongProvider(client=self.network_provider)
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

    def search(self, search_string: str, **kwargs) -> SongSearchIndexType:
        """Search Song using the search string and creates a Song Search data model"""
        search_result: SongListRawType = self.stream_provider.search_songs(
            search_string, **kwargs)
        return self._create_search_song_index(search_result)

    def select(self, selection: int, **kwargs) -> Optional[SongType]:
        """Select Song from the Song Search Index and returns the selected Song"""
        selected_song = self.indexed_search_songs.get(int(selection))
        if selected_song:
            song_url = self.stream_provider.select_song(
                selected_song.token, **kwargs)
            if song_url:
                selected_song.__dict__.update({'stream_url': song_url})
                selected_song.__dict__.update({'status': 'Loaded'})
                return self._create_song(**selected_song.__dict__)
        raise InvalidInput("Invalid song selection input provided.")

    def get_song_url(self, data: str) -> str:
        """Get the song's stream url using Enc Url Token - used for rsongs download"""
        stream_url = self.stream_provider.select_song(data)
        return stream_url

    def get_related_songs(self, data: str) -> list[SongType]:
        """Gets recommended songs using song_id and updates the RQueue"""
        recomm_songs_raw: SongListRawType = self.stream_provider.get_recomm_songs(
            data)
        if recomm_songs_raw:
            return list(map(self._create_recomm_song, recomm_songs_raw))
        return None


class JioSaavnSongQueue(ISongQueue):
    """Song queue implemented for Jio Saavn"""

    def __init__(self) -> None:
        self.queue: SongQueueType = SongQueue([])
        self._indexed_queue = {}
        self.rsongs_copy_ = set()
        self.rsongs_list: list[SongType] = []
        self.current_playing_song = None

    def _check_media(self, song: SongType) -> bool:
        """Checks the presence of media"""
        if song in self.queue.songs:
            return True
        return False

    def _normalize_queue_index(self) -> None:
        """Updates the queue with index"""
        for count, song in enumerate(self.queue.songs, 1):
            self._indexed_queue.update(
                {count: song})

    def add_playlist(self, entity):
        """Add playlist songs"""
        for song in entity.songs:
            if not self._check_media(song):
                self.queue.songs.append(song)
                self._normalize_queue_index()
        print(f"\n\033[01m\033[32mAdded: '{entity.name}'\033[0m")
        # print()

    def change_loaded_status(self):
        """Change loaded status"""
        for song in self.queue.songs:
            if song.status == 'Loaded':
                song.status = '\033[31mPlayed\033[0m'

    def flush_queue(self):
        """Flushes the queue"""
        self.queue.songs.clear()
        self._normalize_queue_index()

    def add(self, entity: SongType) -> bool:
        """Add Song to Queue"""
        if not self._check_media(entity):
            self.queue.songs.append(entity)
            self._normalize_queue_index()
            print(f"\n\033[01m\033[32mAdded: '{entity.name}'\033[0m")
            # print()
        if not self._check_media(entity):
            raise AddMediaError("Failed to add media to queue")
        if entity not in self._indexed_queue.values():
            raise AddMediaError("Failed to add media to queue index")
        return True

    def remove(self, index: int) -> list[SongType]:
        """Remove Songs by Index value"""
        removed_songs = []
        for value in list(index):
            song = self.fetch(value)
            if self._check_media(song):
                self.queue.songs.remove(song)
                self._indexed_queue.pop(int(value))
                removed_songs.append(song)
                print(f"\n\033[93mRemoved: '{song.name}'\033[0m")
                # print()
            else:
                raise MediaNotFound("Media not found in queue to delete")
            if song in self._indexed_queue.values():
                raise RemoveMediaError(
                    "Failed to remove media from queue index")
        self._normalize_queue_index()
        return removed_songs

    def fetch(self, index: int) -> SongType:
        """Fetch the song from Queue Index"""
        song = self._indexed_queue.get(int(index))
        if not song:
            raise GetMediaError("Failed to get media from queue index")
        return song

    def add_related_songs(self, songs: SongListRawType) -> None:
        """Add recommended songs to queue index"""
        queue_length = len(self.queue.songs)
        for song in songs:
            if not self._check_media(song):
                self.queue.songs.append(song)
        for count, song in enumerate(self.queue.songs, queue_length+1):
            self._indexed_queue.update({count: song})

    def update_qstatus(self, status: str, stream_url: str) -> None:
        """Update 'played' status for songs in Queue and returns Song object if it's successful.
        Also, Updates the current_playing_song attr."""
        for song in self.queue.songs:
            if stream_url == song.stream_url:
                self.current_playing_song = song
                if song.status == 'Loaded':
                    print(f"\n\033[31m>>> Playing '{song.name}' <<<\033[0m")
                    song.status = status
                    return song
        return None

    @property
    def get_queue(self) -> SongQueueType:
        """returns song queue"""
        return self.queue

    @property
    def get_indexed_queue(self) -> SongQueueIndexType:
        """returns the indexed queue"""
        return self._indexed_queue

    def check_status(self, queue: SongQueueType):
        """Checks the queue status for 'played' songs"""
        for song in queue.songs:
            if song.status == '\033[31mPlayed\033[0m':
                continue
            else:
                return False
        return True

    def pop_rsong(self):
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
                print(f"\n\033[33mRemoved: '{rsong.name}'\033[0m")
        except IndexError:
            print("Invalid RS Index!")

    @property
    def get_rsongs(self):
        """Get the rsongs list"""
        return self.rsongs_list

    def update_rqueue(self, rsongs: list[SongType]):
        """Update the rsongs list"""
        if not self.rsongs_list:
            self.rsongs_list.extend(rsongs)
        else:
            for song in rsongs:
                if song not in self.rsongs_copy_:
                    self.rsongs_list.append(song)
        self.rsongs_copy_.update(rsongs)
        # SET: making a copy of all rsongs to avoid dups.
