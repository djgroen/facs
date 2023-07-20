"""Module for miscellaneous functions."""

import numpy as np


def probability(prob):
    """Return True with probability prob."""
    return np.random.random() < prob


def get_random_int(high):
    """Return a random integer between 0 and high."""
    return np.random.randint(0, high)
