"""Module for the Household class."""

from __future__ import annotations

import random

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .person import Person
from .utils import probability

if TYPE_CHECKING:
    from .facs import Ecosystem
    from .disease import Disease


HOME_INTERACTION_FRACTION = 0.2
# people are within 2m at home of a specific other person 20% of the time.


@dataclass
class House:
    """Dummy class for House for typehints."""


@dataclass
class Household:
    """Class for Household."""

    house: House
    ages: list[float]
    size: int = -1

    agents: list[Person] = field(default_factory=list, init=False)

    def __post_init__(self):
        """Post init function."""

        if self.size <= -1:
            self.size = random.choice([1, 2, 3, 4])

        for _ in range(self.size):
            self.agents.append(Person(self.house, self, self.ages))

    def get_infectious_count(self):
        """Get the number of infectious people in the household."""
        ic = 0
        for i in range(0, self.size):
            if (
                self.agents[i].status == "infectious"
                and self.agents[i].hospitalised is False
            ):
                ic += 1
        return ic

    def is_infected(self):
        """Check if the household has any infectious people."""

        return self.get_infectious_count() > 0

    def evolve(self, eco: Ecosystem, disease: Disease):
        """Evolve the household."""

        ic = self.get_infectious_count()
        for i in range(0, self.size):
            if self.agents[i].status == "susceptible":
                if ic > 0:
                    infection_chance = (
                        eco.contact_rate_multiplier["house"]
                        * disease.infection_rate
                        * HOME_INTERACTION_FRACTION
                        * ic
                    )
                    # house infection already incorporates airflow, because derived from literature.
                    if probability(infection_chance):
                        self.agents[i].infect(eco)
