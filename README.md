### RK Music Streamer

A command-line music streamer that allows you to stream songs, albums, playlists. <br>
**Powered by [Jio Saavn](https://www.jiosaavn.com) Web APIs**

---
#### Prerequisites
- Python 3.9.x or above.
- VLC player must be installed. This application uses the VLC player for streaming and python-vlc bindings for interaction. <br>
(Install from [VLC](https://www.videolan.org/vlc/))

#### Dependencies
- [requests](https://pypi.org/project/requests/)
- [python-vlc](https://pypi.org/project/python-vlc/)
---
#### Installation
```
> python3 -m pip install rkstreamer
$ pip/pip3 install rkstreamer
```
---
#### Launch
```
Launch the application by entering the following in the terminal:

> python3 -m rkstreamer
or
> rkstreamer

```
---
#### Usage
- Default mode is 'Song Search' Mode.
- Modes can be switched using **--album, --plist**.
- Supports search parameters for Songs, Albums -> 'search string' -n:number, -l:language, -b:bitrate.
- **-q, -r, -g** switch displays Song Queue, Recommended Songs, Go-to-Album modes.
- **a, p, r** followed by the song index can be used to Add, Play, Remove songs from the corresponding queues.

---
#### Controls

- **-c** switch control the player and media playback; supports volume, playback, audio output controls.
- Player control actions should be suffixed with the '-c' switch such as **-cp** - play/pause, **-cs** - stop, **-cn** - next song, **-cpr** - previous song.
- Volume controls: **v** - display current volume, **+(number)** - volume increase, **-(number)** - volume decrease.
- Playback controls: **>(seconds)** - seek forward, **<(seconds)** - seek backward, **t** - show remaining time.
- Audio output controls: **lo** - list output device, **co(index)** - change output to index.

---
#### Examples

```
> Enter the song name: pokkal pokkum -n:5 -l:tamil -b:320
(Search string - pokkal pokkum, number of results to display - 5, language - tamil, bitrate - 320kpbs)

*When a song is playing:
> Enter the song name: -q
(Displays the song queue)
> -r
(Displays the recommended song queue)
> -g
(Displays the playing song's album songs)

> -qr1 - removes the first index song from queue
> -qp1 - plays the first index song from queue
> -qa1 - adds the first index song from search list

Similar behaviors for -r (recommended songs), -g (go-to-album).
Correct prefix and actions should be used such as -rr1, -ga1, etc.
  
Volume Controls:
  -cv - Shows current volume
  -c+10 - Increase volume by 10
  -c-10 - Decrease volume by 10
  -cv100 - Set volume to 100

Playback controls:
  -c>10 - Forward by 10 seconds
  -c<10 - Backward by 10 seconds
  -ct - Show remaining time

```

