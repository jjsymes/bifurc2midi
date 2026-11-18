from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

PIANO_LOWEST_MIDI_NOTE = 21
PIANO_HIGHEST_MIDI_NOTE = 108
_KEYS_ABOVE_THE_LOWEST = PIANO_HIGHEST_MIDI_NOTE - PIANO_LOWEST_MIDI_NOTE
DEFAULT_TICKS_PER_BEAT = 960


class NoteValue(Enum):
    """How many of this value fit in one whole note."""

    WHOLE = 1
    HALF = 2
    QUARTER = 4
    EIGHTH = 8
    SIXTEENTH = 16
    THIRTYSECOND = 32
    SIXTYFOURTH = 64

    def ticks(self, ticks_per_beat: int) -> int:
        return ticks_per_beat * 4 // self.value


@dataclass(frozen=True)
class MusicalEvent:
    pitches: tuple[int, ...]
    duration_ticks: int

    def __post_init__(self) -> None:
        if not self.pitches:
            raise ValueError("a musical event needs at least one pitch")
        if self.duration_ticks <= 0:
            raise ValueError("duration must be positive")
        for pitch in self.pitches:
            _require_midi_pitch(pitch)


@dataclass(frozen=True)
class Score:
    ticks_per_beat: int
    tempo_bpm: int
    pedal_down: bool
    events: tuple[MusicalEvent, ...]


def score_from_columns(
    columns: Sequence[Sequence[float]],
    *,
    arpeggiate: bool = True,
    pedal_down: bool = True,
    tempo_bpm: int = 120,
    note_value: NoteValue = NoteValue.SIXTEENTH,
    ticks_per_beat: int = DEFAULT_TICKS_PER_BEAT,
) -> Score:
    """Map each column of logistic x values to sounding pitches.

    x of 0 is MIDI note 21 (A0) and x of 1 is MIDI note 108 (C8).
    An arpeggio plays the distinct pitches low to high, one note value each.
    Otherwise the pitches of a column sound together for one note value.
    """
    duration_ticks = note_value.ticks(ticks_per_beat)
    events = [
        event
        for column in columns
        for event in _events_for_column(column, arpeggiate, duration_ticks)
    ]
    return Score(
        ticks_per_beat=ticks_per_beat,
        tempo_bpm=tempo_bpm,
        pedal_down=pedal_down,
        events=tuple(events),
    )


def _events_for_column(
    column: Sequence[float],
    arpeggiate: bool,
    duration_ticks: int,
) -> tuple[MusicalEvent, ...]:
    pitches = _pitches_for_points(column)
    if not pitches:
        return ()
    if arpeggiate:
        return tuple(MusicalEvent((pitch,), duration_ticks) for pitch in pitches)
    return (MusicalEvent(pitches, duration_ticks),)


def _pitches_for_points(points: Sequence[float]) -> tuple[int, ...]:
    return tuple(sorted({_pitch_for_x(point) for point in points}))


def _pitch_for_x(x: float) -> int:
    """Half-up map of x onto the 88 piano keys, clamped at the ends."""
    unclamped = PIANO_LOWEST_MIDI_NOTE + int(x * _KEYS_ABOVE_THE_LOWEST + 0.5)
    if unclamped < PIANO_LOWEST_MIDI_NOTE:
        return PIANO_LOWEST_MIDI_NOTE
    if unclamped > PIANO_HIGHEST_MIDI_NOTE:
        return PIANO_HIGHEST_MIDI_NOTE
    return unclamped


def _require_midi_pitch(pitch: int) -> None:
    if pitch < 0 or pitch > 127:
        raise ValueError("pitch must be a MIDI note from 0 to 127")
