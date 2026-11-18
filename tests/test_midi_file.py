from mido import MidiFile, bpm2tempo

from bifurc2midi.adapters.midi_file import save, score_to_midi
from bifurc2midi.domain.music import MusicalEvent, Score


def _chord_score() -> Score:
    return Score(
        ticks_per_beat=960,
        tempo_bpm=120,
        pedal_down=True,
        events=(MusicalEvent((60, 64), 240),),
    )


def _message_rows(score: Score) -> list[tuple[str, int, int, int]]:
    rows = []
    for message in score_to_midi(score).tracks[0]:
        if message.type == "set_tempo":
            continue
        if message.type == "control_change":
            continue
        rows.append((message.type, message.note, message.velocity, message.time))
    return rows


def test_chord_with_pedal_encodes_tempo_sustain_and_shared_duration():
    midi = score_to_midi(_chord_score())
    messages = list(midi.tracks[0])

    assert midi.ticks_per_beat == 960
    assert messages[0].type == "set_tempo"
    assert messages[0].tempo == bpm2tempo(120)
    assert messages[0].time == 0
    assert messages[1].type == "control_change"
    assert messages[1].control == 64
    assert messages[1].value == 127
    assert messages[1].time == 0
    assert _message_rows(_chord_score()) == [
        ("note_on", 60, 64, 0),
        ("note_on", 64, 64, 0),
        ("note_off", 60, 127, 240),
        ("note_off", 64, 127, 0),
    ]


def test_arpeggio_without_pedal_plays_one_note_after_another():
    score = Score(
        ticks_per_beat=480,
        tempo_bpm=90,
        pedal_down=False,
        events=(
            MusicalEvent((60,), 120),
            MusicalEvent((64,), 120),
        ),
    )
    midi = score_to_midi(score)
    messages = list(midi.tracks[0])

    assert midi.ticks_per_beat == 480
    assert messages[0].tempo == bpm2tempo(90)
    assert all(message.type != "control_change" for message in messages)
    assert _message_rows(score) == [
        ("note_on", 60, 64, 0),
        ("note_off", 60, 127, 120),
        ("note_on", 64, 64, 0),
        ("note_off", 64, 127, 120),
    ]


def test_save_round_trips_the_file(tmp_path):
    midi = score_to_midi(_chord_score())
    path = tmp_path / "out.mid"

    save(midi, str(path))

    loaded = MidiFile(str(path))
    original = [(message.type, message.time) for message in midi.tracks[0]]
    loaded_messages = [(message.type, message.time) for message in loaded.tracks[0]]

    assert loaded.ticks_per_beat == midi.ticks_per_beat
    assert loaded_messages[: len(original)] == original
    assert loaded_messages[-1][0] == "end_of_track"
