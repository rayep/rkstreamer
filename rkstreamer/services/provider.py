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

SONG_SEARCH = {'p': 1, 'q': '', 'n': '', '__call': 'search.getResults'} # n - num of results.

SONG_DOWNLOAD = {'__call': 'song.generateAuthToken', 'url': '', 'bitrate': ''} # enc_url, bitrate

ENTITY_STATION = {'__call': 'webradio.createEntityStation', 'entity_id': '',
                  'entity_type': 'queue', 'freemium': '', 'shared': ''}

RECOMM_SONGS = {'__call': 'webradio.getSong', 'stationid': '', 'k': ''} # k - count of rsongs.

PLIST_SEARCH = {'__call': 'search.getPlaylistResults', 'p': 1, 'q': ''}

PLIST_DOWNLOAD = {'__call': 'webapi.get', 'token': '', 'type': 'playlist',
                  'includeMetaTags': 0, 'p': 1, 'n': 50}


class JioSaavnSongProvider(ISongProvider):
    """Jio Saavn - Song provider API"""

    def __init__(self, client: NetworkProviderType) -> None:
        self.client = client

    def search_songs(self, search_string: str, **kwargs):
        """Search songs using the search string"""
        SONG_SEARCH['q'] = quote_plus(search_string)
        SONG_SEARCH['n'] = kwargs.get('num')
        SONG_DOWNLOAD['bitrate'] = kwargs.get('bitrate')
        RECOMM_SONGS['k'] = kwargs.get('rsongs')
        response = self.client.get(
            url=API_BASE, params=SONG_SEARCH|PARAMS_DEFAULT)
        return self._parse_songs(response, lang=kwargs.get('lang'))

    def _parse_songs(self, response: NetworkProviderResponseType, **kwargs) -> SongListRawType:
        """Parsing songs info from search songs call"""
        return [{'name': unescape(song['title']),
                'id': song['id'],
                    'album_name': unescape(song['more_info']['album']),
                    'music': song['more_info']['music'],
                    'artists': song['subtitle'].replace(f" - {song['more_info']['album']}", ''),
                    'duration': song['more_info']['duration'],
                    'token': song['more_info']['encrypted_media_url'],
                    'album_id': song['more_info']['album_url'].split('/')[-1],
                    'status': 'Fetched'}
                for song in response.json()['results'] if song['language'] in kwargs.get('lang')]

    def select_song(self, arg: str, **kwargs):
        SONG_DOWNLOAD['url'] = arg  # Encrypted URL
        response = self.client.get(
            url=API_BASE, params=SONG_DOWNLOAD | PARAMS_DEFAULT)
        return self._parse_song_url(response)

    def _parse_song_url(self, response: NetworkProviderResponseType) -> str:
        """Get the song download URL"""
        auth_url = response.json()['auth_url']
        stream_url = self.client.get(url=auth_url, allow_redirects=False)
        return stream_url.headers['Location']

    def _get_station_id(self, song_id: str):
        ENTITY_STATION['entity_id'] = f'["{song_id}"]'
        sid_response = self.client.get(
            url=API_BASE, params=ENTITY_STATION | PARAMS_DEFAULT)
        sid = sid_response.json()['stationid']
        return sid

    def _parse_recomm_songs(self, response: NetworkProviderResponseType):
        return [{'name': unescape(song['song']['title']),
                'id': song['song']['id'],
                 'album_name': unescape(song['song']['more_info']['album']),
                 'music': song['song']['more_info']['music'],
                 'artists': song['song']['subtitle'].replace(f" - {song['song']['more_info']['album']}", ''),
                 'duration': song['song']['more_info']['duration'],
                 'token': song['song']['more_info']['encrypted_media_url'],
                 'album_id': song['song']['more_info']['album_url'].split('/')[-1],
                 'status': 'Fetched'}
                for key, song in response.json().items() if key != 'stationid']

    def get_recomm_songs(self, song_id: str, **kwargs) -> SongListRawType:
        """Get recommended songs from song_id"""
        station_id = self._get_station_id(song_id)
        RECOMM_SONGS['stationid'] = station_id
        recomm_songs = self.client.get(
            url=API_BASE, params=RECOMM_SONGS | PARAMS_DEFAULT)
        return self._parse_recomm_songs(recomm_songs)


class JioSaavnPlaylistProvider(IPlaylistProvider):
    """Jio Saavn - Playlist provider API"""

    def __init__(self, client: NetworkProviderType) -> None:
        self.client = client

    def search_playlists(self, search_string: str, language: str = 'tamil'):
        """Playlist search"""
        plist_request = self.client.get(
            url=API_BASE, params=PLIST_SEARCH | PARAMS_DEFAULT)
        return self._parse_playlist(plist_request, language)

    def _parse_playlist(self, response: NetworkProviderResponseType, language: str):
        """Parse playlist response"""
        return [{'name': plist['title'],
                'perma_url': plist['perma_url'].split('/')[-1],
                 'song_count': plist['more_info']['song_count']}
                for plist in response.json()['results']
                if plist['more_info']['language'] == language]

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
