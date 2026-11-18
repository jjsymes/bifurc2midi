from unittest.mock import MagicMock

import pytest

from bifurc2midi.adapters.plot import marker_size, plot, points_to_draw
from bifurc2midi.domain.diagram import BifurcationDiagram, Orbit


def test_marker_size_shrinks_as_the_point_limit_grows():
    assert marker_size(None) == 1.0
    assert marker_size(1) == 4.0
    assert marker_size(10) == 4.0
    assert marker_size(11) == 1.0
    assert marker_size(100) == 1.0
    assert marker_size(101) == 0.02


def test_missing_limit_draws_every_point():
    assert points_to_draw((0.1, 0.2, 0.3), None) == (0.1, 0.2, 0.3)


def test_limit_keeps_the_tail_of_the_orbit():
    assert points_to_draw((0.1, 0.2, 0.3), 1) == (0.3,)
    assert points_to_draw((0.1, 0.2, 0.3), 3) == (0.1, 0.2, 0.3)


@pytest.mark.parametrize("limit", [0, -1, 4])
def test_limit_outside_the_orbit_raises(limit):
    with pytest.raises(ValueError, match="point limit"):
        points_to_draw((0.1, 0.2), limit)


def test_empty_diagram_raises(monkeypatch):
    monkeypatch.setattr("bifurc2midi.adapters.plot.plt.show", lambda: None)

    with pytest.raises(ValueError, match="no orbits"):
        plot(BifurcationDiagram(()))


def test_plot_rejects_a_limit_higher_than_an_orbit(monkeypatch):
    monkeypatch.setattr("bifurc2midi.adapters.plot.plt.show", lambda: None)
    diagram = BifurcationDiagram((Orbit(2.0, (0.1, 0.2)),))

    with pytest.raises(ValueError, match="point limit"):
        plot(diagram, point_limit=3)


def test_plot_draws_one_series_per_orbit_and_shows_it(monkeypatch):
    figure = MagicMock()
    axes = MagicMock()
    shown = {"value": False}
    monkeypatch.setattr(
        "bifurc2midi.adapters.plot.plt.subplots",
        lambda: (figure, axes),
    )
    monkeypatch.setattr(
        "bifurc2midi.adapters.plot.plt.show",
        lambda: shown.__setitem__("value", True),
    )
    diagram = BifurcationDiagram(
        (
            Orbit(2.9, (0.1, 0.2, 0.3)),
            Orbit(3.0, (0.4,)),
        )
    )

    plot(diagram)

    assert axes.plot.call_count == 2
    first = axes.plot.call_args_list[0]
    second = axes.plot.call_args_list[1]
    assert first.args == ([2.9, 2.9, 2.9], (0.1, 0.2, 0.3), "b.")
    assert first.kwargs["markersize"] == 1.0
    assert second.args == ([3.0], (0.4,), "b.")
    figure.set_size_inches.assert_called_once_with(16, 9)
    axes.set.assert_called_once_with(
        xlabel="r", ylabel="x", title="Bifurcation Diagram"
    )
    assert shown["value"] is True
