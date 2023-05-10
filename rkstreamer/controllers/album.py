"""Album controller - module"""

import re
from typing import Union
from rkstreamer.controllers.enums import ControllerEnum
from rkstreamer.utils.helper import parse_input
from rkstreamer.controllers.patterns import (
    SongControllerUtils,
    AlbumSearchCommand,
    AlbumSelectCommand,
    AlbumSongSelectCommand,
    PlayerControlsCommand,
    AlbumQueueCommand,
    ReSongQueueCommand)
from rkstreamer.types import (
    AlbumModelType,
    AlbumViewType,
    CommandType
)

class JioSaavnAlbumController(SongControllerUtils):
    """Jio Saavn Controller"""

    def __init__(self, model: AlbumModelType, view: AlbumViewType) -> None:
        self.model = model
        self.view = view
        self.commands = {
            ControllerEnum.QUEUE: AlbumQueueCommand(self),
            ControllerEnum.CONTROLS: PlayerControlsCommand(self),
            ControllerEnum.RQUEUE: ReSongQueueCommand(self),
            'as': AlbumSongSelectCommand(self),
            str: AlbumSearchCommand(self),
            int: AlbumSelectCommand(self),
        }
        super().__init__(model, view)

    def handle_input(self, user_input: Union[str, int]):
        """Handles the user input"""
        if user_input.startswith('-'):
            re_match = re.match(r'(-\w{1})', user_input)
            try:
                enum_obj = ControllerEnum(re_match.group(1))
                command: CommandType = self.commands.get(enum_obj)
                command.execute(user_input)
            except (ValueError, AttributeError):
                print("Invalid input. Please try again")
        else:
            album_selection = re.match(r'[aA](\d+)', user_input)
            if album_selection:
                song_selection = album_selection.group(1)
                command: CommandType = self.commands.get('as')
                command.execute(song_selection)
            else:
                input_type = type(parse_input(user_input))
                command: CommandType = self.commands.get(input_type)
                command.execute(user_input)
