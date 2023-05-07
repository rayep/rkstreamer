"""Module with helper functions & classes"""


def parse_input(input_str: str):
    """Return input based on the type"""
    if input_str.isdigit():
        return int(input_str)
    return input_str

SPACE = r"([\s]+)?"
SONG = r"(?P<song>([\w\s]+))"
ALBUM = r"(?P<album>([\w\s]+))"
LANG = r"(\-[l]:(?P<lang>\w+){1})?"
NUM = r"(\-[n]:(?P<num>\d{1}))?"
BITRATE = r"(\-[b]:(?P<bitrate>(160|320)))?"
RSONGS = r"(\-[r]:(?P<rsongs>\d{1,2}))?"

SONG_PATTERN = SONG+SPACE+LANG+SPACE+NUM+SPACE+BITRATE+SPACE+RSONGS
ALBUM_PATTERN = ALBUM+SPACE+LANG+SPACE+NUM
