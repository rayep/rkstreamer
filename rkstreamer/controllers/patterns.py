"""
Design patterns implementation
"""

import re
from rkstreamer.interfaces.patterns import Command
from rkstreamer.controllers.enums import SongQueueEnum
from rkstreamer.models.exceptions import InvalidInput
from rkstreamer.utils.helper import SONG_PATTERN, ALBUM_PATTERN
from rkstreamer.types import (
    SongControllerType,
    SongModelType,
    SongViewType,
    AlbumControllerType,
    AlbumModelType,
    AlbumViewType,
    CommandType
)


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
                if isinstance(command, SongQueueAddCommand):
                    command.execute(user_input.replace(
                        user_input[0], '').split(','))
                else:
                    command.execute(user_input.replace(
                        user_input[0], ''))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class SongQueueAddCommand(Command):
    """Song Queue - Add command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model

    def execute(self, user_input: str):
        for number in user_input:
            song = self.model.select(int(number))
            self.controller.uow_add_songs_queue(song)


class SongQueueRemoveCommand(Command):
    """Song Queue - Remove command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        songs = self.model.queue.remove(user_input)
        for song in songs:
            self.view.remove_media(song)


class SongQueuePlayCommand(Command):
    """Song Queue - Play command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        song = self.model.queue.fetch(user_input)
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
                if isinstance(command, AlbumQueueAddCommand):
                    command.execute(user_input.replace(
                        user_input[0], '').split(','))
                else:
                    command.execute(user_input.replace(
                        user_input[0], ''))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class AlbumQueueAddCommand(Command):
    """Album Queue - Add command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: AlbumModelType = self.controller.model

    def execute(self, user_input: str):
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
                if isinstance(command, ReSongQueueAddCommand):
                    command.execute(user_input.replace(
                        user_input[0], '').split(','))
                else:
                    command.execute(user_input.replace(user_input[0], ''))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class ReSongQueueAddCommand(Command):
    """RS Queue - Add Command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
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

    def execute(self, user_input: str):
        if len(user_input) > 1:
            print("*Only one song can be delete from RS queue!*")
        else:
            self.model.queue.remove_rsong_index(int(user_input))


class ReSongQueuePlayCommand(Command):
    """Song Queue - Play command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        song = self.model.queue.get_rsong_index(int(user_input))
        if song:
            song.stream_url = self.model.get_song(song.token)
            song.status = 'Loaded'
            self.controller.uow_play_songs_remove_loaded(song)


class PlayerControlsCommand(Command):
    """Player Controls"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        if user_input.lower().startswith('-c'):
            self.view.player_input(user_input.replace('-c', ''))
