from collections.abc import Sequence

import matplotlib.pyplot as plt

from bifurc2midi.domain.diagram import BifurcationDiagram


def marker_size(point_limit: int | None) -> float:
    """Pick a marker size for how many points each r value will draw."""
    if point_limit is None:
        return 1.0
    if point_limit <= 10:
        return 4.0
    if point_limit <= 100:
        return 1.0
    return 0.02


def points_to_draw(points: Sequence[float], limit: int | None) -> tuple[float, ...]:
    """Return the orbit tail to plot, or the whole orbit when there is no limit."""
    if limit is None:
        return tuple(points)
    if limit < 1 or limit > len(points):
        raise ValueError(
            "point limit must be between 1 and the number of points in the orbit"
        )
    return tuple(points[-limit:])


def plot(diagram: BifurcationDiagram, point_limit: int | None = None) -> None:
    """Draw the diagram and show it. The diagram itself is left unchanged."""
    series = _series(diagram, point_limit)
    _draw(series, marker_size(point_limit))
    plt.show()


def _series(
    diagram: BifurcationDiagram,
    point_limit: int | None,
) -> tuple[tuple[float, tuple[float, ...]], ...]:
    if not diagram.orbits:
        raise ValueError("diagram has no orbits to plot")
    return tuple(
        (orbit.r, points_to_draw(orbit.points, point_limit)) for orbit in diagram.orbits
    )


def _draw(
    series: tuple[tuple[float, tuple[float, ...]], ...],
    size: float,
) -> None:
    figure, axes = plt.subplots()
    figure.set_size_inches(16, 9)
    for r, points in series:
        axes.plot([r] * len(points), points, "b.", markersize=size)
    axes.set(xlabel="r", ylabel="x", title="Bifurcation Diagram")
