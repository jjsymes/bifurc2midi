import pytest

from bifurc2midi.domain.music import MusicalEvent, NoteValue, score_from_columns


def test_endpoints_map_onto_the_piano_keys():
    score = score_from_columns([[0.0, 1.0]], arpeggiate=False)

    assert score.events[0].pitches == (21, 108)


def test_half_up_boundary_rounds_away_from_zero():
    just_below_a_half = (10.5 - 1e-9) / 87
    on_the_half = 10.5 / 87

    score = score_from_columns(
        [[just_below_a_half, on_the_half]],
        arpeggiate=False,
    )

    assert score.events[0].pitches == (31, 32)


def test_values_outside_the_unit_interval_clamp_to_the_piano():
    score = score_from_columns([[-0.1, 1.1]], arpeggiate=False)

    assert score.events[0].pitches == (21, 108)


def test_duplicate_pitches_collapse_and_sort_ascending():
    score = score_from_columns([[1.0, 0.0, 0.0, 1.0]], arpeggiate=False)

    assert score.events[0].pitches == (21, 108)


def test_different_x_values_that_share_a_key_collapse():
    score = score_from_columns([[0.0, 0.001]], arpeggiate=False)

    assert score.events[0].pitches == (21,)


def test_arpeggio_plays_each_pitch_in_order_for_one_note_value():
    score = score_from_columns(
        [[1.0, 0.0], [0.5]],
        arpeggiate=True,
        note_value=NoteValue.SIXTEENTH,
    )

    assert [(event.pitches, event.duration_ticks) for event in score.events] == [
        ((21,), 240),
        ((108,), 240),
        ((65,), 240),
    ]


def test_chord_mode_packs_a_column_into_one_event():
    score = score_from_columns(
        [[1.0, 0.0], [0.5]],
        arpeggiate=False,
        note_value=NoteValue.QUARTER,
    )

    assert [(event.pitches, event.duration_ticks) for event in score.events] == [
        ((21, 108), 960),
        ((65,), 960),
    ]


def test_an_empty_column_adds_no_events():
    score = score_from_columns([[], [0.0]], arpeggiate=True)

    assert [event.pitches for event in score.events] == [(21,)]


@pytest.mark.parametrize(
    ("note_value", "expected_ticks"),
    [
        (NoteValue.WHOLE, 3840),
        (NoteValue.HALF, 1920),
        (NoteValue.QUARTER, 960),
        (NoteValue.EIGHTH, 480),
        (NoteValue.SIXTEENTH, 240),
        (NoteValue.THIRTYSECOND, 120),
        (NoteValue.SIXTYFOURTH, 60),
    ],
)
def test_note_value_ticks_at_960_match_the_quarter_note_clock(
    note_value, expected_ticks
):
    assert note_value.ticks(960) == expected_ticks


def test_pedal_and_tempo_are_stored_on_the_score():
    score = score_from_columns(
        [[0.0]],
        pedal_down=False,
        tempo_bpm=72,
        ticks_per_beat=480,
    )

    assert score.pedal_down is False
    assert score.tempo_bpm == 72
    assert score.ticks_per_beat == 480


def test_musical_event_rejects_an_empty_pitch_list():
    with pytest.raises(ValueError, match="at least one pitch"):
        MusicalEvent((), 240)


@pytest.mark.parametrize("duration_ticks", [0, -1])
def test_musical_event_rejects_a_non_positive_duration(duration_ticks):
    with pytest.raises(ValueError, match="duration must be positive"):
        MusicalEvent((60,), duration_ticks)


@pytest.mark.parametrize("pitch", [-1, 128])
def test_musical_event_rejects_pitches_outside_midi(pitch):
    with pytest.raises(ValueError, match="0 to 127"):
        MusicalEvent((pitch,), 240)


@pytest.mark.parametrize("pitch", [0, 127])
def test_musical_event_accepts_the_midi_range_endpoints(pitch):
    assert MusicalEvent((pitch,), 1).pitches == (pitch,)
