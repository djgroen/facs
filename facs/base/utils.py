"""Module for miscellaneous functions."""

import os

import numpy as np


num_infections_today = 0
num_hospitalisations_today = 0
num_deaths_today = 0
num_recoveries_today = 0
log_prefix = "."


def probability(prob):
    """Return True with probability prob."""
    return np.random.random() < prob


def get_random_int(high):
    """Return a random integer between 0 and high."""
    return np.random.randint(0, high)


class OUTPUT_FILES:
    def __init__(self):
        self.files = {}

    def open(self, file_name):
        if not file_name in self.files:
            if os.path.exists(file_name):
                os.remove(file_name)
            self.files[file_name] = open(file_name, "a")

        return self.files[file_name]

    def __del__(self) -> None:
        for out_file in self.files:
            self.files[out_file].close()


out_files = OUTPUT_FILES()


def log_infection(t, x, y, loc_type, rank, phase_duration):
    global num_infections_today
    out_inf = out_files.open("{}/covid_out_infections_{}.csv".format(log_prefix, rank))
    print(
        "{},{},{},{},{},{}".format(t, x, y, loc_type, rank, phase_duration),
        file=out_inf,
        flush=True,
    )
    num_infections_today += 1


def log_hospitalisation(t, x, y, age, rank):
    global num_hospitalisations_today
    out_inf = out_files.open(
        "{}/covid_out_hospitalisations_{}.csv".format(log_prefix, rank)
    )
    print("{},{},{},{}".format(t, x, y, age), file=out_inf, flush=True)
    num_hospitalisations_today += 1


def log_death(t, x, y, age, rank):
    global num_deaths_today
    out_inf = out_files.open("{}/covid_out_deaths_{}.csv".format(log_prefix, rank))
    print("{},{},{},{}".format(t, x, y, age), file=out_inf, flush=True)
    num_deaths_today += 1


def log_recovery(t, x, y, age, rank):
    global num_recoveries_today
    out_inf = out_files.open("{}/covid_out_recoveries_{}.csv".format(log_prefix, rank))

    print("{},{},{},{}".format(t, x, y, age), file=out_inf, flush=True)
    num_recoveries_today += 1
