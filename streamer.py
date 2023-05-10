"""Tests: Display songs"""

import re
from rkstreamer.controllers.enums import CommandEnum
from rkstreamer.services.player import PyVlcPlayer
from rkstreamer.controllers import JioSaavnSongController, JioSaavnAlbumController
from rkstreamer.models import JioSaavnSongModel, JioSaavnAlbumModel
from rkstreamer.views import JioSaavnSongView, JioSaavnAlbumView
from rkstreamer.services.network import PyRequests
from rkstreamer.types import (
    SongControllerType,
    AlbumControllerType
)

proxy = {'https': 'http://127.0.0.1:8888'}
pyrequests = PyRequests(proxy=None)

song_controller = JioSaavnSongController(
    model=JioSaavnSongModel(pyrequests),
    view=JioSaavnSongView(player=PyVlcPlayer())
)

album_controller = JioSaavnAlbumController(
    model=JioSaavnAlbumModel(pyrequests),
    view=JioSaavnAlbumView(player=PyVlcPlayer())
)

print("""
Welcome Ray!

Jio Saavn Streaming Service
""")

controllers = {
    '-s': song_controller,
    '-a': album_controller
}

class StateMachine:
    def __init__(self):
        self.state = None

    def start(self):
        self.state = StartState()

    def handle_input(self, user_input):
        new_state = self.state.handle_input(user_input)
        if new_state:
            self.state = new_state

class StartState:
    def handle_input(self, user_input):
        if user_input == '-s':
            return SongState()
        elif user_input == '-a':
            return AlbumState()
        else:
            print("Invalid state")


class SongState:
    def handle_input(self, user_input):
        # handle user input for song controller
        if user_input == '-a':
            return AlbumState()

class AlbumState:
    def handle_input(self, user_input):
        # handle user input for album controller
        if user_input == '-s':
            return SongState()

while True:

    user_input = input("Enter a selection: ")



# class StreamHandler():
#     """Stream handler class"""

#     def __init__(self, song: SongControllerType, album: AlbumControllerType) -> None:
#         self.song = song
#         self.album = album
#         self.commands = {
#             '-s': song
#         }

#     def handle_input(self, user_input: str):
#         """Handle the user input"""
#         if user_input.startswith('-'):
#             re_match = re.match(r'(-\w{1})', user_input)
#             try:
#                 enum_obj = CommandEnum(re_match.group(1))
#                 command = self.commands.get(enum_obj)
#                 command.handle_input(user_input)
#             except (ValueError, AttributeError):
#                 print("Invalid input. Please try again")


# while True:
#     user_input = input("Enter the song name: ")
#     if user_input:
#         test.handle_input(user_input)
