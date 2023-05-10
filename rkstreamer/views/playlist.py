"""
Playlist view implementation module
"""

from rkstreamer.types import MusicPlayerControlsType
from rkstreamer.views.song import JioSaavnSongView


class JioSaavnPlaylistView(JioSaavnSongView):
    """Jio Saavn Album view"""

    def __init__(self, player: MusicPlayerControlsType) -> None:
        self.player = player
        super().__init__(player)

    def display(self, entity) -> None:
        for count, playlist in entity.items():
            print(f"{count}- {playlist.name}")
            print(f"Song Count - {playlist.song_count}")
            print()

    def display_playlist_songs(self, entity) -> None:
        """Display album songs"""
        for count, song in entity.songs.items():
            print(f"A{count}- {song.name}")
            print()

    def add_media_list(self, songs_list: list):
        """Add songs list to player mlist"""
        return self.player.mlplayer_factory.add_medias(songs_list)

    def play(self):
        """Play the media list"""
        return self.player.mlplayer_controls.play()

    def stop(self):
        """stop the media list"""
        return self.player.mlplayer_controls.stop()
