import random
from collections.abc import Callable
from dataclasses import dataclass

from bifurc2midi.domain.diagram import (
    BifurcationDiagram,
    InitialXBehaviour,
    generate_diagram,
)
from bifurc2midi.domain.music import NoteValue, Score, score_from_columns


@dataclass(frozen=True)
class PerformanceRequest:
    r_start: float
    r_end: float
    r_step_size: float
    iterations: int
    burn_in: int
    initial_x_behaviour: InitialXBehaviour
    initial_x: float | None
    arpeggiate: bool
    pedal_on: bool
    bpm: int
    note_value: NoteValue


@dataclass(frozen=True)
class Performance:
    diagram: BifurcationDiagram
    score: Score


def perform(
    request: PerformanceRequest,
    rng: Callable[[], float] = random.random,
) -> Performance:
    """Generate a diagram and the score played from its columns."""
    diagram = generate_diagram(
        request.r_start,
        request.r_end,
        request.r_step_size,
        request.iterations,
        initial_x=request.initial_x,
        initial_x_behaviour=request.initial_x_behaviour,
        burn_in=request.burn_in,
        rng=rng,
    )
    score = score_from_columns(
        tuple(orbit.points for orbit in diagram.orbits),
        arpeggiate=request.arpeggiate,
        pedal_down=request.pedal_on,
        tempo_bpm=request.bpm,
        note_value=request.note_value,
    )
    return Performance(diagram, score)
