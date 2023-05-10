"""
Design patterns implementation
"""

import re
import threading
from typing import Union
from rkstreamer.interfaces.controllers import ISongController
from rkstreamer.interfaces.patterns import Command
from rkstreamer.controllers.enums import SongQueueEnum
from rkstreamer.models.exceptions import InvalidInput
from rkstreamer.utils.helper import SONG_PATTERN, ALBUM_PATTERN
from rkstreamer.types import (
    SongControllerType,
    SongType,
    SongModelType,
    SongViewType,
    AlbumControllerType,
    AlbumModelType,
    AlbumViewType,
    PlaylistControllerType,
    PlaylistModelType,
    PlaylistViewType,
    CommandType
)


class SongControllerUtils(ISongController):
    """Generic controller utils for handling songs"""

    def __init__(
            self,
            model: Union[SongModelType, AlbumModelType],
            view: Union[SongViewType, AlbumViewType]) -> None:

        self.model = model
        self.view = view

        self.view.set_controller_callback(self.uow_update_song_status)

        _ = threading.Timer(30, self.monitor_queue_pull_rsong)
        _.setDaemon(True)
        _.start()

    def uow_update_song_status(self, status: str, stream_url: str):
        """Updating song status in queue to "Played"
        if the song has been selected to play from search or from queue
        This function fetchs the rsongs for the playing song and updates rsong list."""
        song = self.model.queue.update_qstatus(status, stream_url)
        if song and len(self.model.queue.get_rsongs) <= 50:
            self.uow_add_rsongs_rqueue(song.id)

    def monitor_queue_pull_rsong(self):
        """Pull rsong by monitoring the queue songs status"""
        if self.model.queue.check_status(self.model.queue.get_queue):
            get_rsong = self.model.queue.pop_rsong()
            if get_rsong:
                get_rsong.stream_url = self.model.get_song(get_rsong.token)
                self.uow_add_songs_queue(get_rsong)
        threading.Timer(45, self.monitor_queue_pull_rsong).start()

    def uow_add_songs_queue(self, song: SongType):
        """UOW: Add songs to queue & media list. Doesn't play it"""
        self.model.queue.add(song)
        self.view.add_media(song)

    def uow_add_rsongs_rqueue(self, data: str):
        """UOW: Add Recommended songs to RQueue
        :data - song_id"""
        recomm_songs = self.model.get_related_songs(data)
        if recomm_songs:
            self.model.queue.update_rqueue(recomm_songs)

    def uow_play_songs_remove_loaded(self, song: SongType):
        """UOW: Calls add queue with 'remove_loaded: true' &
        play the media"""
        self.model.queue.change_loaded_status()
        self.view.play_media(song)


class AlbumSearchCommand(Command):
    """Album Search"""

    def __init__(self, controller: AlbumControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model
        self.view: AlbumViewType = self.controller.view

    def execute(self, user_input: str):
        match_input = re.match(ALBUM_PATTERN, user_input)
        album = match_input.group('album').strip()
        match_input.groupdict().pop('album')
        search_results = self.model.search(album, **match_input.groupdict())
        self.view.display(search_results)


class AlbumSelectCommand(Command):
    """Song Select command implementation"""

    def __init__(self, controller: AlbumControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model
        self.view: AlbumViewType = self.controller.view

    def execute(self, user_input: int):
        album = self.model.select(int(user_input))
        self.view.display_album_songs(album)


class AlbumSongSelectCommand(Command):
    """Song Select command implementation"""

    def __init__(self, controller: AlbumControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model
        self.view: AlbumViewType = self.controller.view

    def execute(self, user_input: int):
        album_song = self.model.select_song_from_album(int(user_input))
        self.controller.uow_play_songs_remove_loaded(album_song)


class SongSearchCommand(Command):
    """Song Search command implementation"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        match_input = re.match(SONG_PATTERN, user_input)
        song = match_input.group('song').strip()
        match_input.groupdict().pop('song')
        search_results = self.model.search(song, **match_input.groupdict())
        self.view.display(search_results)


class SongSelectCommand(Command):
    """Song Select command implementation"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        song = self.model.select(user_input)
        self.controller.uow_play_songs_remove_loaded(song)


class SongQueueCommand(Command):
    """Song Queue command implementation"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view
        self.commands = {
            SongQueueEnum.ADD: SongQueueAddCommand(self.controller),
            SongQueueEnum.REMOVE: SongQueueRemoveCommand(self.controller),
            SongQueueEnum.PLAY: SongQueuePlayCommand(self.controller)
        }

    def execute(self, user_input: str):
        if user_input == '-q':
            queue = self.model.queue.get_indexed_queue
            self.view.display_queue(queue)
        elif len(user_input) > 2:
            user_input = user_input.replace('-q', '')
            try:
                enum_obj = SongQueueEnum(user_input[0])
                command: CommandType = self.commands.get(enum_obj)
                command.execute(user_input.replace(
                        user_input[0], '').split(','))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class SongQueueAddCommand(Command):
    """Song Queue - Add command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model

    def execute(self, user_input: list):
        for number in user_input:
            song = self.model.select(int(number))
            self.controller.uow_add_songs_queue(song)


class SongQueueRemoveCommand(Command):
    """Song Queue - Remove command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: list):
        songs = self.model.queue.remove(user_input)
        for song in songs:
            self.view.remove_media(song)


class SongQueuePlayCommand(Command):
    """Song Queue - Play command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: list):
        song = self.model.queue.fetch(user_input[0])
        self.controller.uow_play_songs_remove_loaded(song)


class AlbumQueueCommand(Command):
    """Album queue command"""

    def __init__(self, controller: AlbumControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model
        self.view: AlbumViewType = self.controller.view
        self.commands = {
            SongQueueEnum.ADD: AlbumQueueAddCommand(self.controller),
            SongQueueEnum.REMOVE: SongQueueRemoveCommand(self.controller),
            SongQueueEnum.PLAY: SongQueuePlayCommand(self.controller)
        }

    def execute(self, user_input: str):
        if user_input == '-q':
            queue = self.model.queue.get_indexed_queue
            self.view.display_queue(queue)
        elif len(user_input) > 2:
            user_input = user_input.replace('-q', '')
            try:
                enum_obj = SongQueueEnum(user_input[0])
                command: CommandType = self.commands.get(enum_obj)
                command.execute(user_input.replace(
                    user_input[0], '').split(','))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class AlbumQueueAddCommand(Command):
    """Album Queue - Add command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model

    def execute(self, user_input: list):
        for number in user_input:
            song = self.model.select_song_from_album(int(number))
            self.controller.uow_add_songs_queue(song)


class ReSongQueueCommand(Command):
    """Recommended songs - Queue Command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view
        self.commands = {
            SongQueueEnum.ADD: ReSongQueueAddCommand(self.controller),
            SongQueueEnum.REMOVE: ReSongQueueRemoveCommand(self.controller),
            SongQueueEnum.PLAY: ReSongQueuePlayCommand(self.controller)
        }

    def execute(self, user_input: str):
        if user_input == '-r':
            queue = self.model.queue.get_rsongs
            self.view.display_rsongs_queue(queue)
        elif len(user_input) > 2:
            user_input = user_input.replace('-r', '')
            try:
                enum_obj = SongQueueEnum(user_input[0])
                command: CommandType = self.commands.get(enum_obj)
                command.execute(user_input.replace(
                        user_input[0], '').split(','))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class ReSongQueueAddCommand(Command):
    """RS Queue - Add Command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: list):
        for number in user_input:
            rsong = self.model.queue.get_rsong_index(int(number))
            rsong.stream_url = self.model.get_song(rsong.token)
            rsong.status = 'Loaded'
            self.controller.uow_add_songs_queue(rsong)


class ReSongQueueRemoveCommand(Command):
    """RS Queue - Remove Command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: list):
        if len(user_input) > 1:
            print("*Only one song can be delete from RS queue!*")
        else:
            self.model.queue.remove_rsong_index(int(user_input[0]))


class ReSongQueuePlayCommand(Command):
    """Song Queue - Play command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: list):
        song = self.model.queue.get_rsong_index(int(user_input[0]))
        if song:
            song.stream_url = self.model.get_song(song.token)
            song.status = 'Loaded'
            self.controller.uow_play_songs_remove_loaded(song)


class PlaylistSelectCommand(Command):
    """Playlist Select command implementation"""

    def __init__(self, controller: PlaylistControllerType):
        self.controller = controller
        self.model: PlaylistModelType = self.controller.model
        self.view: PlaylistViewType = self.controller.view

    def execute(self, user_input: int):
        playlist = self.model.select(user_input)
        self.controller.uow_play_songs(playlist)


class PlaylistSearchCommand(Command):
    """Album Search"""

    def __init__(self, controller: AlbumControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model
        self.view: AlbumViewType = self.controller.view

    def execute(self, user_input: str):
        search_results = self.model.search(user_input)
        self.view.display(search_results)


class PlayerControlsCommand(Command):
    """Player Controls"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        if user_input.lower().startswith('-c'):
            self.view.player_input(user_input.replace('-c', ''))
