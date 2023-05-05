"""Controller Implementation module"""

import threading
import re
from typing import Union
from rkstreamer.types import (
    SongType,
    SongModelType,
    SongViewType,
    CommandType
)
from rkstreamer.interfaces.controllers import ISongController
from rkstreamer.controllers.patterns import (
    SongSearchCommand,
    SongSelectCommand,
    SongQueueCommand,
    ReSongQueueCommand,
    PlayerControlsCommand)
from rkstreamer.utils.helper import parse_input
from rkstreamer.controllers.enums import SongEnum


class JioSaavnSongController(ISongController):
    """Song Controller implemented for Jio Saavn model"""

    def __init__(self, model: SongModelType, view: SongViewType) -> None:
        self.model = model
        self.view = view
        self.commands = {
            SongEnum.QUEUE: SongQueueCommand(self),
            SongEnum.CONTROLS: PlayerControlsCommand(self),
            SongEnum.RQUEUE: ReSongQueueCommand(self),
            str: SongSearchCommand(self),
            int: SongSelectCommand(self),
        }
        self.view.set_controller_callback(self.uow_update_song_status)

        _ = threading.Timer(30, self.monitor_queue_pull_rsong)
        _.setDaemon(True)
        _.start()

    def handle_input(self, user_input: Union[str, int]):
        if user_input.startswith('-'):
            re_match = re.match(r'(-\w{1})', user_input)
            try:
                enum_obj = SongEnum(re_match.group(1))
                command: CommandType = self.commands.get(enum_obj)
                command.execute(user_input)
            except (ValueError, AttributeError):
                print("Invalid input. Please try again")
        else:
            input_type = type(parse_input(user_input))
            command: CommandType = self.commands.get(input_type)
            command.execute(user_input)

    def uow_update_song_status(self, status: str, stream_url: str):
        """Updating song status in queue to "Played"
        if the song has been selected to play from search or from queue
        This function fetchs the rsongs for the playing song and updates rsong list."""
        song = self.model.queue.update_qstatus(status, stream_url)
        if song:
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
        self.model.queue.update_rqueue(recomm_songs)

    def uow_play_songs_remove_loaded(self, song: SongType):
        """UOW: Calls add queue with 'remove_loaded: true' &
        play the media"""
        self.model.queue.add(song, change_loaded=True)
        self.view.play_media(song)
