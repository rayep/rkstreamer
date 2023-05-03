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
from rkstreamer.interfaces.provider import ISongProvider
disable_warnings()  # Function to suppress the SSL Verification error.

API_BASE = "https://www.jiosaavn.com/api.php"

SONG_SEARCH = {'p': '1', 'q': '', '_format': 'json',
               '_marker': '0', 'ctx': 'web6dot0',
               'n': 3, 'api_version': '4', '__call': 'search.getResults'}

SONG_DOWNLOAD = {'__call': 'song.generateAuthToken', 'url': '',
                 'bitrate': 160, 'api_version': 4,
                 '_format': 'json', 'ctx': 'web6dot0', '_marker': 0}

ENTITY_STATION = {'__call': 'webradio.createEntityStation', 'entity_id': '',
                  'entity_type': 'queue', 'freemium': '', 'shared': '',
                  'api_version': 4, '_format': 'json', '_marker': 0, 'ctx': 'web6dot0'}

RECOMM_SONGS = {'__call': 'webradio.getSong', 'stationid': '', 'k': 5,
                'api_version': 4, '_format': 'json', '_marker': 0,
                'ctx': 'web6dot0'}


class JioSaavnSongProvider(ISongProvider):
    """Jio Saavn - Song provider API"""

    def __init__(self, client: NetworkProviderType) -> None:
        self.client = client

    def search_songs(self, search_string):
        """Search songs using the search string"""
        SONG_SEARCH['q'] = quote_plus(search_string)
        response = self.client.get(url=API_BASE, params=SONG_SEARCH)
        return self._parse_songs(response)

    def _parse_songs(self, response: NetworkProviderResponseType) -> SongListRawType:
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
                for song in response.json()['results']]

    def select_song(self, arg: str):
        SONG_DOWNLOAD['url'] = arg # Encrypted URL
        response = self.client.get(url=API_BASE, params=SONG_DOWNLOAD)
        return self._parse_song_url(response)

    def _parse_song_url(self, response: NetworkProviderResponseType) -> str:
        """Get the song download URL"""
        auth_url = response.json()['auth_url']
        stream_url = self.client.get(url=auth_url, allow_redirects=False)
        return stream_url.headers['Location']

    def _get_station_id(self, song_id: str):
        ENTITY_STATION['entity_id'] = f'["{song_id}"]'
        sid_response = self.client.get(url=API_BASE, params=ENTITY_STATION)
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

    def get_recomm_songs(self, song_id: str) -> SongListRawType:
        """Get recommended songs from song_id"""
        station_id = self._get_station_id(song_id)
        RECOMM_SONGS['stationid'] = station_id
        recomm_songs = self.client.get(url=API_BASE, params=RECOMM_SONGS)
        return self._parse_recomm_songs(recomm_songs)
