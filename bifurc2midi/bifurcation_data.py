from enum import Enum
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from bifurc2midi.logistic_map import logistic_map_output


class LogisticMapInitialXValueBehaviour(Enum):
    STATIC = "static"
    RANDOM_EACH_ITERATION = "random_each_iteration"
    LAST_LOGISTIC_MAP_X = "last_logistic_map_x"

    def __str__(self):
        return self.value


class BifurcationData:
    x_values = np.zeros(0, dtype=np.ndarray)
    r_values = np.zeros(0)

    @classmethod
    def from_raw_data(cls, r_values: np.ndarray, x_values: np.ndarray):
        if len(r_values) != len(x_values):
            raise ValueError("r_values and x_values must be the same length")
        if x_values.dtype != np.ndarray:
            raise ValueError("x_values must be a numpy array of numpy arrays")
        bifurcation_data = cls()
        bifurcation_data.r_values = r_values
        bifurcation_data.x_values = x_values
        return bifurcation_data

    @classmethod
    def from_data_generation_parameters(
        cls,
        r_start: float,
        r_end: float,
        r_step_size: float,
        number_of_iterations_per_r_value: int,
        x_initial: float = float(np.random.rand()),
        x_initial_behaviour: LogisticMapInitialXValueBehaviour = LogisticMapInitialXValueBehaviour.STATIC,
        burn_in: Optional[int] = None,
    ):
        bifurcation_data = cls()
        bifurcation_data.generate(
            r_start,
            r_end,
            r_step_size,
            number_of_iterations_per_r_value,
            x_initial,
            x_initial_behaviour,
            burn_in,
        )
        return bifurcation_data

    def transform_x_values(self, transform_function) -> None:
        for i, x_value_list in enumerate(self.x_values):
            self.x_values[i] = list(map(transform_function, x_value_list))

    def transform_r_values(self, transform_function) -> None:
        for i, r_value in enumerate(self.r_values):
            self.r_values[i] = transform_function(r_value)

    def remove_duplicate_x_values(self) -> None:
        for i, x_value_list in enumerate(self.x_values):
            self.x_values[i] = list(set(x_value_list))

    def plot(self, desired_num_plots_per_r_value: Optional[int] = None) -> None:
        if len(self.r_values) != len(self.x_values):
            raise ValueError("r_values and x_values must be the same length.")
        if desired_num_plots_per_r_value and desired_num_plots_per_r_value > len(
            self.x_values[0]
        ):
            raise ValueError(
                "desired_num_plots_per_r_value is higher than the number of data points available for each r value."
            )
        if desired_num_plots_per_r_value is None:
            marker_size = 1.0
        elif desired_num_plots_per_r_value <= 10:
            marker_size = 4.0
        elif desired_num_plots_per_r_value <= 100:
            marker_size = 1.0
        else:
            marker_size = 0.02
        fig, biax = plt.subplots()
        fig.set_size_inches(16, 9)
        for i, r in enumerate(self.r_values):
            if desired_num_plots_per_r_value is None:
                num_plots_per_r_value = len(self.x_values[i])
            index_of_first_x_to_plot = len(self.x_values[i]) - num_plots_per_r_value

            x_axis = np.full(num_plots_per_r_value, r)
            y_axis = self.x_values[i][index_of_first_x_to_plot:]
            biax.plot(x_axis, y_axis, "b.", markersize=marker_size)
        biax.set(xlabel="r", ylabel="x", title="Bifurcation Diagram")
        plt.show()

    def generate(
        self,
        r_start: float,
        r_end: float,
        r_step_size: float,
        number_of_iterations_per_r_value: int,
        x_initial: float = float(np.random.rand()),
        x_initial_behaviour: LogisticMapInitialXValueBehaviour = LogisticMapInitialXValueBehaviour.STATIC,
        burn_in: Optional[int] = None,
    ):
        self.r_values, self.x_values = self._generate(
            r_start,
            r_end,
            r_step_size,
            number_of_iterations_per_r_value,
            x_initial=x_initial,
            x_initial_behaviour=x_initial_behaviour,
            burn_in=burn_in,
        )

    def _generate(
        self,
        r_start: float,
        r_end: float,
        r_step_size: float,
        number_of_iterations_per_r_value: int,
        x_initial: float = float(np.random.rand()),
        x_initial_behaviour: LogisticMapInitialXValueBehaviour = LogisticMapInitialXValueBehaviour.STATIC,
        burn_in: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        r_number_of_values = int((r_end - r_start) / r_step_size)
        r_values = np.linspace(r_start, r_end, r_number_of_values)
        x_values = np.zeros(len(r_values), dtype=np.ndarray)
        if burn_in is None:
            burn_in = number_of_iterations_per_r_value // 2
        if burn_in >= number_of_iterations_per_r_value:
            raise ValueError(
                "burn_in must be less than number_of_iterations_per_r_value"
            )

        for i, r in enumerate(r_values):
            x_values[i] = logistic_map_output(
                r, x_initial, number_of_iterations_per_r_value, burn_in=burn_in
            )

            if (
                x_initial_behaviour
                == LogisticMapInitialXValueBehaviour.RANDOM_EACH_ITERATION
            ):
                x_initial = float(np.random.rand())
            elif (
                x_initial_behaviour
                == LogisticMapInitialXValueBehaviour.LAST_LOGISTIC_MAP_X
            ):
                # perhaps LAST_LOGISTIC_MAP_X systemically biases starting x values
                # to one branch of the bifurcation diagram
                x_initial = x_values[i][-1]

        return r_values, x_values

    def __len__(self):
        return len(self.r_values)
