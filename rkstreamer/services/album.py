"""
Albums provider - API
"""

from html import unescape
from urllib.parse import quote_plus
from urllib3 import disable_warnings
from rkstreamer.interfaces.provider import IAlbumProvider
from rkstreamer.types import (
    NetworkProviderType,
    NetworkProviderResponseType)
disable_warnings()  # Function to suppress the SSL Verification error.


class JioSaavnAlbumProvider(IAlbumProvider):
    """Jio Saavn Album provider API"""

    API_BASE = "https://www.jiosaavn.com/api.php"

    PARAMS_DEFAULT = {'api_version': 4, '_format': 'json', '_marker': 0,
                      'ctx': 'web6dot0'}

    album_search = {'__call': 'search.getAlbumResults',
                    'n': 3, 'p': 1, 'q': ''}

    album_select = {'__call': 'webapi.get', 'token': '',
                    'type': 'album', 'includeMetaTags': 0}

    def __init__(self, client: NetworkProviderType) -> None:
        self.client = client

    def search_albums(self, search_string: str, **kwargs):
        self.album_search['q'] = quote_plus(search_string)
        self.album_search['n'] = kwargs.get('num') or 3
        language = [kwargs.get('lang'),] \
            if kwargs.get('lang') \
                else ['tamil', 'english', 'hindi', 'telugu', 'kannada', 'spanish', 'latin']
        response = self.client.get(
            url=self.API_BASE, params=self.album_search | self.PARAMS_DEFAULT)
        return self._parse_albums(response, lang=language)

    def _parse_albums(self, response: NetworkProviderResponseType, **kwargs):
        return [{'name': unescape(album['title']),
                'id': album['perma_url'].split('/')[-1],
                 'music': album['more_info']['music'][:50] if album['more_info']['music'] else '',
                 'artists': unescape(album['subtitle']),
                 'song_count': album['more_info']['song_count']}
                for album in response.json()['results'] if album['language'] in kwargs.get('lang')]

    def select_album(self, arg: str, **kwargs):
        self.album_select['token'] = arg
        response = self.client.get(
            url=self.API_BASE, params=self.album_select | self.PARAMS_DEFAULT)
        return self._parse_album_songs(response)

    def _parse_album_songs(self, response: NetworkProviderResponseType):
        return [{'name': unescape(song['title']),
                 'id': song['id'],
                 'album_name': unescape(song['more_info']['album']),
                 'music': song['more_info']['music'][:50] if song['more_info']['music'] else '',
                 'artists': unescape(song['subtitle'].replace(f" - {song['more_info']['album']}", '')),
                 'duration': song['more_info']['duration'],
                 'token': song['more_info']['encrypted_media_url'],
                 'album_id': song['more_info']['album_url'].split('/')[-1]}
                for song in response.json()['list']]
