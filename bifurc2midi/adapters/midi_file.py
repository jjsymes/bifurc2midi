from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from bifurc2midi.domain.music import MusicalEvent, Score

SUSTAIN_PEDAL = 64
SUSTAIN_PEDAL_DOWN = 127
NOTE_ON_VELOCITY = 64
NOTE_OFF_VELOCITY = 127


def score_to_midi(score: Score) -> MidiFile:
    """Encode a score as a single-track MIDI file."""
    midi_file = MidiFile(ticks_per_beat=score.ticks_per_beat)
    track = MidiTrack()
    midi_file.tracks.append(track)
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(score.tempo_bpm), time=0))
    if score.pedal_down:
        track.append(
            Message(
                "control_change",
                control=SUSTAIN_PEDAL,
                value=SUSTAIN_PEDAL_DOWN,
                time=0,
            )
        )
    for event in score.events:
        _append_event(track, event)
    return midi_file


def save(midi: MidiFile, filename: str) -> None:
    midi.save(filename)


def _append_event(track: MidiTrack, event: MusicalEvent) -> None:
    for pitch in event.pitches:
        track.append(Message("note_on", note=pitch, velocity=NOTE_ON_VELOCITY, time=0))
    for index, pitch in enumerate(event.pitches):
        delta = event.duration_ticks if index == 0 else 0
        track.append(
            Message("note_off", note=pitch, velocity=NOTE_OFF_VELOCITY, time=delta)
        )
