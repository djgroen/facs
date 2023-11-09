"""Module for miscellaneous functions."""

import os

import numpy as np

LOG_PREFIX = "."


def probability(prob):
    """Return True with probability prob."""

    if prob < 0 or prob > 1:
        raise ValueError("prob must be between 0 and 1")

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


def log_infection(t, x, y, loc_type, rank, phase_duration):
    """Log an infection event."""
    # pylint: disable=too-many-arguments

    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_infections_{rank}.csv")
    print(
        f"{t},{x},{y},{loc_type},{rank},{phase_duration}",
        file=out_inf,
        flush=True,
    )
    return 1


def log_hospitalisation(t, x, y, age, rank):
    """Log a hospitalisation event."""

    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_hospitalisations_{rank}.csv")
    print(f"{t},{x},{y},{age}", file=out_inf, flush=True)
    return 1


def log_death(t, x, y, age, rank):
    """Log a death event."""

    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_deaths_{rank}.csv")
    print(f"{t},{x},{y},{age}", file=out_inf, flush=True)
    return 1


def log_recovery(t, x, y, age, rank):
    """Log a recovery event."""
    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_recoveries_{rank}.csv")

    print(f"{t},{x},{y},{age}", file=out_inf, flush=True)
    return 1


def calc_dist(x1, y1, x2, y2):
    """Return the distance between two points."""
    return (np.abs(x1 - x2) ** 2 + np.abs(y1 - y2) ** 2) ** 0.5


def calc_dist_cheap(x1, y1, x2, y2):
    return np.abs(x1 - x2) + np.abs(y1 - y2)


def write_log_headers(rank):
    """Write the headers for the log files."""

    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_infections_{rank}.csv")
    print("#time,x,y,location_type,rank,incubation_time", file=out_inf, flush=True)
    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_hospitalisations_{rank}.csv")
    print("#time,x,y,age", file=out_inf, flush=True)
    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_deaths_{rank}.csv")
    print("#time,x,y,age", file=out_inf, flush=True)
    out_inf = out_files.open(f"{LOG_PREFIX}/covid_out_recoveries_{rank}.csv")
    print("#time,x,y,age", file=out_inf, flush=True)


def check_vac_eligibility(a):
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
