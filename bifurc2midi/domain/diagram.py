import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from bifurc2midi.domain.logistic_map import logistic_map_output


class InitialXBehaviour(Enum):
    """How the next orbit chooses its starting x."""

    def __new__(cls, value: str, description: str) -> "InitialXBehaviour":
        member = object.__new__(cls)
        member._value_ = value
        member.__doc__ = description
        return member

    STATIC = ("static", "Reuse one initial x for every r value.")
    RANDOM_EACH_ITERATION = (
        "random_each_iteration",
        "Draw a new initial x for each r value after the first.",
    )
    LAST_LOGISTIC_MAP_X = (
        "last_logistic_map_x",
        "Seed each orbit from the previous orbit's last x. "
        "This can bias later orbits toward one branch.",
    )


@dataclass(frozen=True)
class Orbit:
    r: float
    points: tuple[float, ...]


@dataclass(frozen=True)
class BifurcationDiagram:
    orbits: tuple[Orbit, ...]

    def __len__(self) -> int:
        return len(self.orbits)


def generate_diagram(
    r_start: float,
    r_end: float,
    r_step_size: float,
    iterations: int,
    initial_x: float | None = None,
    initial_x_behaviour: InitialXBehaviour = InitialXBehaviour.STATIC,
    burn_in: int | None = None,
    rng: Callable[[], float] = random.random,
) -> BifurcationDiagram:
    """Build a bifurcation diagram by iterating the logistic map across r."""
    samples = _r_samples(r_start, r_end, r_step_size)
    if burn_in is None:
        burn_in = iterations // 2
    starting_x = rng() if initial_x is None else initial_x
    orbits = _orbits(samples, iterations, burn_in, starting_x, initial_x_behaviour, rng)
    return BifurcationDiagram(orbits)


def _r_samples(start: float, end: float, step: float) -> tuple[float, ...]:
    _require_positive_step(step)
    _require_ordered_finite_range(start, end)
    samples: list[float] = []
    index = 0
    while True:
        value = start + index * step
        if value > end + step * 1e-9:
            break
        samples.append(value)
        index += 1
    return tuple(samples)


def _require_positive_step(step: float) -> None:
    if not math.isfinite(step) or step <= 0:
        raise ValueError("r step size must be positive")


def _require_ordered_finite_range(start: float, end: float) -> None:
    if not math.isfinite(start) or not math.isfinite(end) or end < start:
        raise ValueError("r end must be greater than or equal to r start")


def _orbits(
    samples: tuple[float, ...],
    iterations: int,
    burn_in: int,
    starting_x: float,
    initial_x_behaviour: InitialXBehaviour,
    rng: Callable[[], float],
) -> tuple[Orbit, ...]:
    orbits: list[Orbit] = []
    x = starting_x
    last_index = len(samples) - 1
    for index, r in enumerate(samples):
        points = tuple(logistic_map_output(r, x, iterations, burn_in=burn_in))
        orbits.append(Orbit(r, points))
        if index < last_index:
            x = _initial_x_for_next_orbit(initial_x_behaviour, x, points, rng)
    return tuple(orbits)


def _initial_x_for_next_orbit(
    behaviour: InitialXBehaviour,
    current_x: float,
    points: tuple[float, ...],
    rng: Callable[[], float],
) -> float:
    if behaviour is InitialXBehaviour.RANDOM_EACH_ITERATION:
        return rng()
    if behaviour is InitialXBehaviour.LAST_LOGISTIC_MAP_X:
        return points[-1]
    return current_x
