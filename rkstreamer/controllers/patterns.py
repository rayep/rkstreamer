"""
Design patterns implementation
"""
from rkstreamer.types import (
    SongControllerType,
    SongModelType,
    SongViewType,
    CommandType
)
from rkstreamer.interfaces.patterns import Command
from rkstreamer.controllers.enums import SongQueueEnum
from rkstreamer.models.exceptions import InvalidInput


class SongSearchCommand(Command):
    """Song Search command implementation"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        search_results = self.model.search_songs(user_input)
        self.view.display_songs(search_results)


class SongSelectCommand(Command):
    """Song Select command implementation"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        song = self.model.select_song(user_input)
        self.model.queue.add_song(song)
        self.view.play_media(song)
        # self.controller.uow_get_rsongs(song.id)


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
                if command:
                    command.execute(user_input.replace(user_input[0], ''))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class SongQueueAddCommand(Command):
    """Song Queue - Add command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        user_input = list(user_input)
        for number in user_input:
            song = self.model.select_song(number)
            self.controller.uow_add_songs_queue(song)


class SongQueueRemoveCommand(Command):
    """Song Queue - Remove command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        songs = self.model.queue.remove_song(user_input)
        for song in songs:
            self.view.remove_media(song)


class SongQueuePlayCommand(Command):
    """Song Queue - Play command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: int):
        song = self.model.queue.fetch_song(user_input)
        self.view.play_media(song)
        # self.controller.uow_add_rsongs(song.id)


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
            self.view.display_rsong_queue(queue)
        elif len(user_input) > 2:
            user_input = user_input.replace('-r', '')
            try:
                enum_obj = SongQueueEnum(user_input[0])
                command: CommandType = self.commands.get(enum_obj)
                if command:
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
        user_input = list(user_input)
        for number in user_input:
            rsong = self.model.queue.get_rsong_index(int(number))
            rsong.stream_url = self.model.select_song_using_eurl(rsong.token)
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
            song.stream_url = self.model.select_song_using_eurl(song.token)
            self.model.queue.add_song(song)
            self.view.play_media(song)


class PlayerControlsCommand(Command):
    """Player Controls"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        if user_input.lower().startswith('-c'):
            self.view.player_input(user_input.replace('-c', ''))
