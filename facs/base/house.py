"""Module for the House class."""

from __future__ import annotations
import sys

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from .household import Household
from .location import Location
from .utils import get_random_int, calc_dist
from .location_types import building_types, building_types_data

if TYPE_CHECKING:
    from .facs import Ecosystem
    from .disease import Disease


@dataclass
class House:
    """Class for House."""

    location_x: float
    location_y: float
    households: list[Household] = field(default_factory=list)
    nearest_locations: list[list[Location]] = field(default_factory=list)
    num_agents: int = 0
    total_size: int = 0

    def add_households(
        self, household_size: int, ages: list[float], num_households: int
    ):
        """Add households to the house."""

        for _ in range(num_households):
            size = 1 + np.random.poisson(household_size - 1)
            self.total_size += size
            self.households.append(Household(self, ages, size))

    def increment_num_agents(self):
        """Add an agent to the house."""

        self.num_agents += 1

    def evolve(self, e: Ecosystem, disease: Disease):
        """Evolve the house."""

        for household in self.households:
            household.evolve(e, disease)

    def find_nearest_locations(self, e: Ecosystem):
        """
        identify preferred locations for each particular purpose,
        and store in an array.

        Takes into account distance, and to a lesser degree size.
        """
        n = []
        ni = []
        for l in building_types:
            if l not in e.locations.keys():
                n.append(None)
                print("WARNING: location type missing")

            if min([element.sqm for element in e.locations[l]]) <= 0:
                print("WARNING: location type with 0 sqm")
                print(f"type: {l}")
                print(
                    "These errors are commonly caused by corruptions in the <building>.csv file."
                )
                print("To detect these, you can use the following command:")
                print('cat <buildings file name>.csv | grep -v house | grep ",0$"')
                sys.exit()

            scaled_distances = [
                calc_dist(self.location_x, self.location_y, element.x, element.y)
                / np.sqrt(element.sqm)
                for element in e.locations[l]
            ]
            sorted_indices = sorted(
                range(len(scaled_distances)), key=lambda k: scaled_distances[k]
            )
            num_neighbours = building_types_data[l]["neighbours"]
            sorted_indices_truncated = sorted_indices[:num_neighbours]

            if building_types_data[l]["fixed"]:
                sorted_indices_truncated = list(
                    np.random.choice(sorted_indices_truncated, 1)
                )

            n.append([e.locations[l][i] for i in sorted_indices_truncated])
            ni.append(sorted_indices_truncated)

        self.nearest_locations = n
        return ni

    def add_infection(self, e, severity="exposed"):
        """Pre-seed infections in the house."""

        # could target using age later on

        hh = int(get_random_int(len(self.households)))
        p = get_random_int(len(self.households[hh].agents))
        if self.households[hh].agents[p].status == "susceptible":
            # because we do pre-seeding we need to ensure we add exactly 1 infection.
            self.households[hh].agents[p].infect(e, severity)
            return True
        return False

    def has_age_susceptible(self, age: int) -> bool:
        """Check if the house has an agent of a given age."""

        for household in self.households:
            for agent in household.agents:
                if agent.age == age:
                    if age.status == "susceptible":
                        return True
        return False

    def add_infection_by_age(self, e, age):
        """Add an infection to the house by age."""

        for hh in self.households:
            for a in hh.agents:
                if a.age == age:
                    if a.status == "susceptible":
                        a.infect(e, severity="exposed")
