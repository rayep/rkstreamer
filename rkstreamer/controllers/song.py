"""Controller Implementation module"""

import re
from typing import Union
from rkstreamer.utils.helper import parse_input
from rkstreamer.controllers.enums import ControllerEnum
from rkstreamer.controllers.patterns import (
    SongControllerUtils,
    SongSearchCommand,
    SongSelectCommand,
    SongQueueCommand,
    ReSongQueueCommand,
    PlayerControlsCommand)
from rkstreamer.types import (
    SongModelType,
    SongViewType,
    CommandType
)


class JioSaavnSongController(SongControllerUtils):
    """Song Controller implemented for Jio Saavn model"""

    def __init__(self, model: SongModelType, view: SongViewType) -> None:
        self.model = model
        self.view = view
        self.commands = {
            ControllerEnum.QUEUE: SongQueueCommand(self),
            ControllerEnum.CONTROLS: PlayerControlsCommand(self),
            ControllerEnum.RQUEUE: ReSongQueueCommand(self),
            str: SongSearchCommand(self),
            int: SongSelectCommand(self),
        }
        super().__init__(model,view)

    def handle_input(self, user_input: Union[str, int]):
        if user_input.startswith('-'):
            re_match = re.match(r'(-\w{1})', user_input)
            try:
                enum_obj = ControllerEnum(re_match.group(1))
                command: CommandType = self.commands.get(enum_obj)
                command.execute(user_input)
            except (ValueError, AttributeError):
                print("Invalid input. Please try again")
        else:
            input_type = type(parse_input(user_input))
            command: CommandType = self.commands.get(input_type)
            command.execute(user_input)
