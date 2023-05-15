from typing import List


def validate_x_initial(x_initial: float) -> None:
    if x_initial < 0 or x_initial > 1:
        print(x_initial)
        raise ValueError("x_initial must be between 0 and 1")


def logistic_function(x: float, r: float) -> float:
    return r * x * (1 - x)


def logistic_map_output(
    r_parameter: float, x_initial: float, number_of_iterations: int, burn_in: int = 0
) -> List[float]:
    """
    x_{n+1} = r.x_{n}.(1-x_{n})
    :param r_parameter r parameter value to use to generate the logistic map
    :param x_initial: initial value of x
    :param number_of_iterations: number of iterations to run the logistic map for
    :param burn_in: number of iterations to discard before returning the output, defaults to
    :returns: array of x values
    :raises ValueError: raises an exception if x_initial is not between 0 and 1 or
    if burn_in is greater than or equal to number_of_iterations
    """
    validate_x_initial(x_initial)
    if burn_in >= number_of_iterations:
        raise ValueError("burn_in must be less than number_of_iterations")

    successive_x_values = []
    x = x_initial
    for i in range(number_of_iterations):
        x = logistic_function(x, r_parameter)
        if i >= burn_in:
            successive_x_values.append(x)
    return successive_x_values
