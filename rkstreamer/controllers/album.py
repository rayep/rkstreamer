"""Album controller - module"""

import re
import threading
from typing import Union
from rkstreamer.interfaces.controllers import IAlbumController
from rkstreamer.controllers.patterns import (
    AlbumSearchCommand,
    AlbumSelectCommand,
    AlbumSongSelectCommand,
    PlayerControlsCommand,
    AlbumQueueCommand,
    ReSongQueueCommand)
from rkstreamer.controllers.enums import ControllerEnum
from rkstreamer.utils.helper import parse_input
from rkstreamer.types import (
    AlbumModelType,
    AlbumViewType,
    CommandType
)

class JioSaavnAlbumController(IAlbumController):
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
        self.view.set_controller_callback(self.uow_update_song_status)

        _ = threading.Timer(30, self.monitor_queue_pull_rsong)
        _.setDaemon(True)
        _.start()

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
            album_selection = re.match(r'[aA](\d+)', user_input)
            if album_selection:
                song_selection = album_selection.group(1)
                command: CommandType = self.commands.get('as')
                command.execute(song_selection)
            else:
                input_type = type(parse_input(user_input))
                command: CommandType = self.commands.get(input_type)
                command.execute(user_input)

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

    def uow_add_songs_queue(self, song):
        """UOW: Add songs to queue & media list. Doesn't play it"""
        self.model.queue.add(song)
        self.view.add_media(song)

    def uow_add_rsongs_rqueue(self, data: str):
        """UOW: Add Recommended songs to RQueue
        :data - song_id"""
        recomm_songs = self.model.get_related_songs(data)
        self.model.queue.update_rqueue(recomm_songs)

    def uow_play_songs_remove_loaded(self, song):
        """UOW: Calls add queue with 'remove_loaded: true' &
        play the media"""
        self.model.queue.add(song, change_loaded=True)
        self.view.play_media(song)
