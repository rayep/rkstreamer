"""Tests: Display album songs"""

from rkstreamer.services.player import PyVlcPlayer
from rkstreamer.controllers.album import JioSaavnAlbumController
from rkstreamer.models.album import JioSaavnAlbumModel
from rkstreamer.views.album import JioSaavnAlbumView
from rkstreamer.services.network import PyRequests

proxy = {'https': 'http://127.0.0.1:8888'}
pyrequests = PyRequests(proxy=None)

test = JioSaavnAlbumController(
    model=JioSaavnAlbumModel(pyrequests),
    view=JioSaavnAlbumView(player=PyVlcPlayer()))

while True:
    user_input = input("Enter the album name: ")
    if user_input:
        test.handle_input(user_input)
