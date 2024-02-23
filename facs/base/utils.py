"""Module for miscellaneous functions."""

from __future__ import annotations

import os

from typing import TYPE_CHECKING
from warnings import warn

import numpy as np

if TYPE_CHECKING:
    from .person import Person

LOG_PREFIX = "."


def probability(prob):
    """Return True with probability prob."""

    if prob < 0 or prob > 1:
        warn(f"Probability (currently {prob}) must be between 0 and 1.")

    return np.random.random() < prob


def get_random_int(high) -> int:
    """Return a random integer between 0 and high."""

    if high < 0:
        raise ValueError("high must be greater than 0")

    return np.random.randint(0, high)


class OutputFiles:
    """Class to manage output files."""

    def __init__(self):
        self.files = {}

    def open(self, file_name):
        """Return a file handle for the given file name."""

        if not file_name in self.files:
            if os.path.exists(file_name):
                os.remove(file_name)

            # pylint: disable=consider-using-with
            self.files[file_name] = open(file_name, "a", encoding="utf-8")

        return self.files[file_name]

    def __del__(self) -> None:
        for _, value in self.files.items():
            value.close()


out_files = OutputFiles()


def log_to_file(category: str, rank: int, data: list[int | float | str]):
    """Log data to a file."""

    out_file = out_files.open(f"{LOG_PREFIX}/covid_out_{category}_{rank}.csv")
    data = ",".join([str(x) for x in data])
    print(data, file=out_file, flush=True)


def log_infection(
    t: int, x: float, y: float, loc_type: str, rank: int, phase_duration: int
) -> int:
    """Log an infection event."""
    # pylint: disable=too-many-arguments

    data = [t, x, y, loc_type, rank, phase_duration]
    log_to_file("infections", rank, data)
    return 1


def log_hospitalisation(t: int, x: float, y: float, age: int, rank: int) -> int:
    """Log a hospitalisation event."""

    data = [t, x, y, age]
    log_to_file("hospitalisations", rank, data)
    return 1


def log_death(t: int, x: float, y: float, age: int, rank: int) -> int:
    """Log a death event."""

    data = [t, x, y, age]
    log_to_file("deaths", rank, data)
    return 1


def log_recovery(t: int, x: float, y: float, age: int, rank: int) -> int:
    """Log a recovery event."""

    data = [t, x, y, age]
    log_to_file("recoveries", rank, data)
    return 1


def calc_dist(x1: float, y1: float, x2: float, y2: float) -> float:
    """Return the distance between two points."""
    return (np.abs(x1 - x2) ** 2 + np.abs(y1 - y2) ** 2) ** 0.5


def write_log_headers(rank) -> None:
    """Write the headers for the log files."""

    data = ["#time", "x", "y", "location_type", "rank", "incubation_time"]
    log_to_file("infections", rank, data)

    data = ["#time", "x", "y", "age"]
    log_to_file("hospitalisations", rank, data)

    data = ["#time", "x", "y", "age"]
    log_to_file("deaths", rank, data)

    data = ["#time", "x", "y", "age"]
    log_to_file("recoveries", rank, data)


def check_vac_eligibility(a: Person) -> bool:
    """Check if an agent is eligible for vaccination."""

    if (
        a.status == "susceptible"
        and a.symptoms_suppressed is False
        and a.antivax is False
    ):
        return True
    return False


def get_interpolated_lists(interpolated_size: int, data: list[list[float]]) -> list:
    """Return interpolated lists of data."""

    interpolated_data = [0.0] * interpolated_size
    data = np.asarray(data)
    for age in range(interpolated_size):
        interpolated_data[age] = np.interp(age, data[:, 0], data[:, 1])

    return interpolated_data
