### RK Music Streamer

A command-line music player that allows you to play/stream songs, albums, playlists.
Powered by Jio Saavn Web APIs.

---
##### Installation
```
> python3 -m pip install rkstreamer
$ pip/pip3 install rkstreamer
```
---
##### Launch
```
Launch the application by entering the following in the terminal:

> python3 -m rkstreamer
or
> rkstreamer

```
---
##### Usage
- Default mode is 'Song Search' Mode.
- Modes can be switched using --album, --plist.
- Supports search parameters for Songs, Albums -> 'search string' -n:number, -l:language, -b:bitrate.
- -q, -r, -g displays Song Queue, Recommended Songs, Go-to-Album modes.
- a, p, r followed by the song index can be used to Add, Play, Remove songs from the corresponding queues.

---
##### Examples

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
