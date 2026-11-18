from dataclasses import replace

import pytest
from mido import MidiFile

from bifurc2midi.adapters.midi_file import save, score_to_midi
from bifurc2midi.application.perform import PerformanceRequest, perform
from bifurc2midi.domain.diagram import InitialXBehaviour
from bifurc2midi.domain.music import NoteValue, score_from_columns

_REQUEST = PerformanceRequest(
    r_start=2.0,
    r_end=3.0,
    r_step_size=1.0,
    iterations=3,
    burn_in=0,
    initial_x_behaviour=InitialXBehaviour.STATIC,
    initial_x=0.25,
    arpeggiate=True,
    pedal_on=False,
    bpm=100,
    note_value=NoteValue.EIGHTH,
)


def test_perform_scores_the_diagram_without_changing_its_points():
    performance = perform(_REQUEST)

    assert performance.diagram.orbits[0].points == (0.375, 0.46875, 0.498046875)
    assert performance.score == score_from_columns(
        tuple(orbit.points for orbit in performance.diagram.orbits),
        arpeggiate=True,
        pedal_down=False,
        tempo_bpm=100,
        note_value=NoteValue.EIGHTH,
    )
    assert all(
        0.0 <= point <= 1.0
        for orbit in performance.diagram.orbits
        for point in orbit.points
    )


def test_perform_draws_a_missing_initial_x_from_the_rng():
    drawn = iter((0.25,))

    performance = perform(
        replace(_REQUEST, initial_x=None, iterations=1),
        rng=lambda: next(drawn),
    )

    assert performance.diagram.orbits[0].points[0] == pytest.approx(2.0 * 0.25 * 0.75)


def test_exported_midi_keeps_the_diagram_in_the_logistic_range(tmp_path):
    performance = perform(_REQUEST)
    points_before = tuple(orbit.points for orbit in performance.diagram.orbits)
    path = tmp_path / "tiny.mid"

    save(score_to_midi(performance.score), str(path))

    loaded = MidiFile(str(path))
    note_ons = [message for message in loaded.tracks[0] if message.type == "note_on"]
    assert note_ons
    assert all(21 <= message.note <= 108 for message in note_ons)
    assert tuple(orbit.points for orbit in performance.diagram.orbits) == points_before
    assert all(0.0 <= point <= 1.0 for points in points_before for point in points)
