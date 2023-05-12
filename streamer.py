"""Tests: Display songs"""

from rkstreamer.services.player import PyVlcPlayer
from rkstreamer.services.network import PyRequests
from rkstreamer.controllers import (
    JioSaavnSongController,
    JioSaavnAlbumController,
    JioSaavnPlaylistController
)
from rkstreamer.models import (
    JioSaavnSongModel,
    JioSaavnAlbumModel,
    JioSaavnPlaylistModel
)
from rkstreamer.views import (
    JioSaavnSongView,
    JioSaavnAlbumView,
    JioSaavnPlaylistView
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

plist_controller = JioSaavnPlaylistController(
    model=JioSaavnPlaylistModel(pyrequests),
    view=JioSaavnPlaylistView(player=PyVlcPlayer())
)

print(r"""

*** RK Streamer ***

@Powered by Jio Saavn

""")


class State:
    """State class"""

    def __init__(self, name, prompt, controller):
        self.name = name
        self.prompt = prompt
        self.controller = controller

    def handle_input(self, user_input):
        """Handle user input"""
        self.controller.handle_input(user_input)


song = State(
    "song",
    "Enter the song name: ",
    song_controller
)

album = State(
    "album",
    "Enter the album name: ",
    album_controller
)

playlist = State(
    "plist",
    "Enter the playlist name: ",
    plist_controller
)


class StateMachine:
    """State machine"""

    def __init__(self):
        self.states = {'song': song, 'album': album, 'plist': playlist}
        self.current_state = song
        self.current_state_name = 'song'

    def trigger(self):
        """Triggers the state change or handle current state"""
        while True:
            user_input = input(self.current_state.prompt)
            if user_input.lower().startswith('-e'):
                raise SystemExit('Tata!')
            elif user_input.startswith("--"):
                state_name = user_input[2:]
                if (state_name != self.current_state_name) and (state_name in self.states):
                    self.current_state.controller.view.stop() # stop player when switching mode.
                    self.current_state = self.states[state_name]
                    self.current_state_name = state_name
            else:
                if user_input:
                    self.current_state.handle_input(user_input)


machine = StateMachine()
machine.trigger()
