"""
Design patterns implementation
"""

import re
from rkstreamer.interfaces.patterns import Command
from rkstreamer.controllers.enums import SongQueueEnum
from rkstreamer.models.exceptions import InvalidInput
from rkstreamer.utils.helper import PATTERN
from rkstreamer.types import (
    SongControllerType,
    SongModelType,
    SongViewType,
    CommandType
)


class SongSearchCommand(Command):
    """Song Search command implementation"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model
        self.view: SongViewType = self.controller.view

    def execute(self, user_input: str):
        match_input = re.match(PATTERN, user_input)
        song = match_input.group('song')

        lang = [match_input.group('lang'),] \
            if match_input.group('lang') \
            else ['tamil', 'english', 'hindi', 'telugu', 'kannada']

        num = match_input.group('num') if match_input.group('num') else 3

        bitrate = match_input.group('bitrate') \
            if match_input.group('bitrate') \
            else 160

        rsongs = match_input.group(
            'rsongs') if match_input.group('rsongs') else 10

        search_results = self.model.search(
            song,
            lang=lang,
            num=num,
            bitrate=bitrate,
            rsongs=rsongs)
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
                if command:
                    command.execute(user_input.replace(user_input[0], ''))
            except ValueError:
                raise InvalidInput("Invalid Queue input provided") from None


class SongQueueAddCommand(Command):
    """Song Queue - Add command"""

    def __init__(self, controller: SongControllerType):
        self.controller = controller
        self.model: SongModelType = self.controller.model

    def execute(self, user_input: str):
        user_input = list(user_input)
        for number in user_input:
            song = self.model.select(number)
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
        self.view.play_media(song)


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
