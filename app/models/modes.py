from enum import Enum


class Modes(Enum):
    ALBUM = "album"
    SONG = "song"


def get_mode_values():
    return [e.value for e in Modes]
