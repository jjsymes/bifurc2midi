import pytest

from bifurc2midi.domain.logistic_map import logistic_map_output


def test_returns_hand_computed_iterations():
    points = logistic_map_output(
        r_parameter=2.0,
        x_initial=0.25,
        number_of_iterations=3,
    )

    assert points == [0.375, 0.46875, 0.498046875]


def test_length_is_iterations_minus_burn_in():
    points = logistic_map_output(
        r_parameter=2.0,
        x_initial=0.25,
        number_of_iterations=5,
        burn_in=2,
    )

    assert len(points) == 3


def test_burn_in_drops_the_prefix():
    full_orbit = logistic_map_output(
        r_parameter=2.0,
        x_initial=0.25,
        number_of_iterations=4,
    )

    burned_in = logistic_map_output(
        r_parameter=2.0,
        x_initial=0.25,
        number_of_iterations=4,
        burn_in=2,
    )

    assert burned_in == full_orbit[2:]


@pytest.mark.parametrize("x_initial", [0.0, 1.0])
def test_accepts_endpoints_of_the_unit_interval(x_initial):
    points = logistic_map_output(
        r_parameter=2.0,
        x_initial=x_initial,
        number_of_iterations=2,
    )

    assert len(points) == 2


@pytest.mark.parametrize("x_initial", [-0.1, 1.1])
def test_rejects_x_outside_the_unit_interval_without_printing(x_initial, capsys):
    with pytest.raises(ValueError, match="between 0 and 1"):
        logistic_map_output(
            r_parameter=2.0,
            x_initial=x_initial,
            number_of_iterations=3,
        )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize(
    ("burn_in", "number_of_iterations"),
    [(3, 3), (4, 3), (-1, 3)],
)
def test_rejects_burn_in_that_does_not_leave_a_suffix(burn_in, number_of_iterations):
    with pytest.raises(ValueError, match="burn_in must be less than"):
        logistic_map_output(
            r_parameter=2.0,
            x_initial=0.25,
            number_of_iterations=number_of_iterations,
            burn_in=burn_in,
        )
