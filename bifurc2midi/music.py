from enum import Enum


class NoteValue(Enum):
    WHOLE = 1
    HALF = 1 / 2
    QUARTER = 1 / 4
    EIGHTH = 1 / 8
    SIXTEENTH = 1 / 16
    THIRTYSECOND = 1 / 32
    SIXTYFOURTH = 1 / 64
