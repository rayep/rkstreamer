"""
Playlist provider - API
"""

"""
Stream Provider - JioSaavn API
"""

from html import unescape
from urllib.parse import quote_plus
from urllib3 import disable_warnings
from rkstreamer.types import (
    SongListRawType,
    NetworkProviderType,
    NetworkProviderResponseType
)
from rkstreamer.interfaces.provider import ISongProvider, IPlaylistProvider
disable_warnings()  # Function to suppress the SSL Verification error.

API_BASE = "https://www.jiosaavn.com/api.php"

PARAMS_DEFAULT = {'api_version': 4, '_format': 'json', '_marker': 0,
                  'ctx': 'web6dot0'}
PARAMS_FTEXT = {'api_version': 4, '_format': 'text', '_marker': 0,
                'ctx': 'web6dot0'}  # Format set to text for plist songs download.

# n - num of results.
SONG_SEARCH = {'p': 1, 'q': '', 'n': '', '__call': 'search.getResults'}

SONG_DOWNLOAD = {'__call': 'song.generateAuthToken',
                 'url': '', 'bitrate': ''}  # enc_url, bitrate

ENTITY_STATION = {'__call': 'webradio.createEntityStation', 'entity_id': '',
                  'entity_type': 'queue', 'freemium': '', 'shared': ''}

# k - count of rsongs.
RECOMM_SONGS = {'__call': 'webradio.getSong', 'stationid': '', 'k': ''}

PLIST_SEARCH = {'__call': 'search.getPlaylistResults', 'p': 1, 'q': ''}

PLIST_DOWNLOAD = {'__call': 'webapi.get', 'token': '', 'type': 'playlist',
                  'includeMetaTags': 0, 'p': 1, 'n': 50}

class JioSaavnPlaylistProvider(IPlaylistProvider):
    """Jio Saavn - Playlist provider API"""

    def __init__(self, client: NetworkProviderType) -> None:
        self.client = client

    def search_playlists(self, search_string: str, **kwargs):
        """Playlist search"""
        PLIST_SEARCH['q'] = search_string
        plist_request = self.client.get(
            url=API_BASE, params=PLIST_SEARCH | PARAMS_DEFAULT)
        return self._parse_playlist(plist_request, **kwargs)

    def _parse_playlist(self, response: NetworkProviderResponseType, **kwargs):
        """Parse playlist response"""
        return [{'name': plist['title'],
                'perma_url': plist['perma_url'].split('/')[-1],
                 'song_count': plist['more_info']['song_count']}
                for plist in response.json()['results']
                if plist['more_info']['language'] == kwargs.get('lang')]

    def select_playlist(self, arg: str):
        PLIST_DOWNLOAD['token'] = arg
        plist_select = self.client.get(
            url=API_BASE, params=PLIST_DOWNLOAD | PARAMS_FTEXT)
        return self._parse_playlist_songs(plist_select)

    def _parse_playlist_songs(self, response: NetworkProviderResponseType, **kwargs):
        """Parse songs from playlist selection"""
        if kwargs.get('view'):
            return [{'name': song['song_for_player']}
                    for song in response.json()['fullsongs']]

        return [{'name': song['song_for_player'],
                'url': self._change_plist_song_url(song['download_url'])}
                for song in response.json()['fullsongs']]

    def _change_plist_song_url(self, song_url: str):
        """Change plist song urls with latest JS CDN host"""
        if 'SAR' in song_url:  # for handling URLs - https://h.saavncdn.com/*/SAR-*.mp3
            return song_url
        rm_pattern = song_url.removeprefix(
            'http://h.saavncdn.com').removeprefix('https://h.saavncdn.com').removesuffix('.mp3')
        new_pattern = "https://aac.saavncdn.com"+rm_pattern+"_96.mp4"
        return new_pattern