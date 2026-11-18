def logistic_map_output(
    r_parameter: float,
    x_initial: float,
    number_of_iterations: int,
    burn_in: int = 0,
) -> list[float]:
    """Return the logistic-map orbit after discarding the burn-in prefix.

    The map is x(n+1) = r * x(n) * (1 - x(n)).
    """
    _require_unit_interval(x_initial)
    _require_burn_in_before_the_end(burn_in, number_of_iterations)
    return _orbit_after_burn_in(r_parameter, x_initial, number_of_iterations, burn_in)


def _require_unit_interval(x_initial: float) -> None:
    if x_initial < 0 or x_initial > 1:
        raise ValueError("x_initial must be between 0 and 1")


def _require_burn_in_before_the_end(burn_in: int, number_of_iterations: int) -> None:
    if burn_in < 0 or burn_in >= number_of_iterations:
        raise ValueError("burn_in must be less than number_of_iterations")


def _orbit_after_burn_in(
    r_parameter: float,
    x_initial: float,
    number_of_iterations: int,
    burn_in: int,
) -> list[float]:
    points: list[float] = []
    x = x_initial
    for iteration in range(number_of_iterations):
        x = r_parameter * x * (1 - x)
        if iteration >= burn_in:
            points.append(x)
    return points
