"""Tests: Search songs"""

from rkstreamer.services.network import PyRequests
from rkstreamer.services.stream import JioSaavnSongService


test = JioSaavnSongService(client=PyRequests(verify=False))
search = test.search_songs('pokkal pokkum')
assert search[0].items()
print(search[0].items())
