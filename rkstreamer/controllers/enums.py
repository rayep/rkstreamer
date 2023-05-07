"""Enum types for Controllers"""

from enum import Enum


class CommandEnum(Enum):
    """Command types"""
    SONG = '-s'
    ALBUM = '-a'
    PLAYLIST = '-p'
    CHART = '-c'


class ControllerEnum(Enum):
    """Song enums"""
    SEARCH = str
    SELECT = int
    QUEUE = '-q'
    CONTROLS = '-c'
    RQUEUE = '-r'
    GTALBUM = '-g'


class SongQueueEnum(Enum):
    """Song Queue Enum"""
    ADD = 'a'
    REMOVE = 'r'
    PLAY = 'p'
