import math

import pytest

from bifurc2midi.domain.diagram import InitialXBehaviour, generate_diagram
from bifurc2midi.domain.music import score_from_columns


def test_default_span_uses_an_exact_step_and_includes_both_ends():
    diagram = generate_diagram(
        r_start=2.9,
        r_end=4.0,
        r_step_size=0.001,
        iterations=1,
        burn_in=0,
        initial_x=0.5,
    )

    assert len(diagram) == 1101
    assert diagram.orbits[0].r == pytest.approx(2.9)
    assert diagram.orbits[-1].r == pytest.approx(4.0)
    assert diagram.orbits[1].r - diagram.orbits[0].r == pytest.approx(0.001)


def test_static_initial_x_is_reused_for_every_orbit():
    def fail_if_called() -> float:
        raise AssertionError("static behaviour should not draw from rng")

    diagram = generate_diagram(
        r_start=2.0,
        r_end=3.0,
        r_step_size=1.0,
        iterations=1,
        burn_in=0,
        initial_x=0.25,
        initial_x_behaviour=InitialXBehaviour.STATIC,
        rng=fail_if_called,
    )

    assert [orbit.points for orbit in diagram.orbits] == [
        (2.0 * 0.25 * 0.75,),
        (3.0 * 0.25 * 0.75,),
    ]


def test_omitted_initial_x_is_drawn_once_per_call():
    drawn = iter((0.25, 0.5))

    def rng() -> float:
        return next(drawn)

    first = generate_diagram(
        r_start=2.0,
        r_end=2.0,
        r_step_size=1.0,
        iterations=1,
        burn_in=0,
        rng=rng,
    )
    second = generate_diagram(
        r_start=2.0,
        r_end=2.0,
        r_step_size=1.0,
        iterations=1,
        burn_in=0,
        rng=rng,
    )

    assert first.orbits[0].points == (2.0 * 0.25 * 0.75,)
    assert second.orbits[0].points == (2.0 * 0.5 * 0.5,)


def test_random_each_iteration_keeps_the_first_x_then_draws():
    drawn = iter((0.4,))

    def rng() -> float:
        return next(drawn)

    diagram = generate_diagram(
        r_start=2.0,
        r_end=3.0,
        r_step_size=1.0,
        iterations=1,
        burn_in=0,
        initial_x=0.25,
        initial_x_behaviour=InitialXBehaviour.RANDOM_EACH_ITERATION,
        rng=rng,
    )

    assert diagram.orbits[0].points == (2.0 * 0.25 * 0.75,)
    assert diagram.orbits[1].points == (3.0 * 0.4 * 0.6,)


def test_last_logistic_map_x_seeds_the_next_orbit():
    def fail_if_called() -> float:
        raise AssertionError("last-x behaviour should not draw from rng")

    diagram = generate_diagram(
        r_start=2.0,
        r_end=3.0,
        r_step_size=1.0,
        iterations=3,
        burn_in=0,
        initial_x=0.25,
        initial_x_behaviour=InitialXBehaviour.LAST_LOGISTIC_MAP_X,
        rng=fail_if_called,
    )

    assert diagram.orbits[0].points == (0.375, 0.46875, 0.498046875)
    assert diagram.orbits[1].points[0] == pytest.approx(
        3.0 * 0.498046875 * (1 - 0.498046875)
    )


def test_default_burn_in_is_half_the_iterations():
    default = generate_diagram(
        r_start=2.0,
        r_end=2.0,
        r_step_size=1.0,
        iterations=5,
        initial_x=0.25,
    )
    explicit = generate_diagram(
        r_start=2.0,
        r_end=2.0,
        r_step_size=1.0,
        iterations=5,
        burn_in=2,
        initial_x=0.25,
    )

    assert default.orbits[0].points == explicit.orbits[0].points
    assert len(default.orbits[0].points) == 3


def test_a_range_that_is_a_single_r_value_has_one_orbit():
    diagram = generate_diagram(
        r_start=2.5,
        r_end=2.5,
        r_step_size=0.1,
        iterations=1,
        burn_in=0,
        initial_x=0.5,
    )

    assert [orbit.r for orbit in diagram.orbits] == [2.5]


@pytest.mark.parametrize("step", [0.0, -0.1, math.nan, math.inf])
def test_bad_step_raises(step):
    with pytest.raises(ValueError, match="step size must be positive"):
        generate_diagram(
            r_start=0.0,
            r_end=1.0,
            r_step_size=step,
            iterations=1,
            burn_in=0,
            initial_x=0.5,
        )


def test_reversed_range_raises():
    with pytest.raises(ValueError, match="greater than or equal to r start"):
        generate_diagram(
            r_start=1.0,
            r_end=0.0,
            r_step_size=0.1,
            iterations=1,
            burn_in=0,
            initial_x=0.5,
        )


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (0.0, math.nan),
        (0.0, math.inf),
        (math.nan, 1.0),
        (math.inf, 1.0),
    ],
)
def test_empty_or_non_finite_r_grid_raises(start, end):
    with pytest.raises(ValueError, match="r end"):
        generate_diagram(
            r_start=start,
            r_end=end,
            r_step_size=0.1,
            iterations=1,
            burn_in=0,
            initial_x=0.5,
        )


def test_scoring_leaves_the_diagram_points_in_the_logistic_range():
    diagram = generate_diagram(
        r_start=2.0,
        r_end=3.0,
        r_step_size=1.0,
        iterations=4,
        burn_in=0,
        initial_x=0.25,
    )
    points_before = tuple(orbit.points for orbit in diagram.orbits)

    score_from_columns(points_before)

    assert tuple(orbit.points for orbit in diagram.orbits) == points_before
    assert all(0.0 <= point <= 1.0 for points in points_before for point in points)


def test_behaviour_values_stay_compatible_with_the_existing_cli():
    assert InitialXBehaviour.STATIC.value == "static"
    assert InitialXBehaviour.RANDOM_EACH_ITERATION.value == "random_each_iteration"
    assert InitialXBehaviour.LAST_LOGISTIC_MAP_X.value == "last_logistic_map_x"
    assert "bias" in (InitialXBehaviour.LAST_LOGISTIC_MAP_X.__doc__ or "").lower()
