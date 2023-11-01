"""Module for the House class."""


import sys

from dataclasses import dataclass, field

import numpy as np

from .household import Household
from .location import Location
from .utils import get_random_int, calc_dist
from .location_types import building_types


@dataclass
class House:
    """Class for House."""

    location_x: float
    location_y: float
    households: list[Household] = field(default_factory=list)
    nearest_locations: list[list[Location]] = field(default_factory=list)
    num_agents: int = 0
    total_size: int = 0

    def add_households(self, household_size, ages, num_households):
        """Add households to the house."""

        for _ in range(num_households):
            size = 1 + np.random.poisson(household_size - 1)
            self.total_size += size
            self.households.append(Household(self, ages, size))

    def increment_num_agents(self):
        """Add an agent to the house."""

        self.num_agents += 1

    def evolve(self, e, disease):
        """Evolve the house."""

        for household in self.households:
            household.evolve(e, disease)

    def find_nearest_locations(self, e):
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
            elif l == "office":  # offices are picked randomly, not based on proximity.
                nearest_loc_index = get_random_int(len(e.locations[l]))

                n.append(e.locations[l][nearest_loc_index])
                ni.append(nearest_loc_index)
            else:
                min_score = 99999.0
                nearest_loc_index = 0
                for k, element in enumerate(
                    e.locations[l]
                ):  # using 'element' to avoid clash with Ecosystem e.
                    # d = calc_dist_cheap(self.x, self.y, element.x, element.y)
                    if element.sqm > 0:
                        d = calc_dist(
                            self.location_x, self.location_y, element.x, element.y
                        ) / np.sqrt(element.sqm)
                        if d < min_score:
                            min_score = d
                            nearest_loc_index = k
                    else:
                        print("ERROR: location found with 0 sqm area.")
                        print(
                            "name: {}, x: {}, y: {}, position in array: {}, type: {}".format(
                                element.name, element.x, element.y, k, l
                            )
                        )
                        print(
                            "These errors are commonly caused by corruptions in the <building>.csv file."
                        )
                        print("To detect these, you can use the following command:")
                        print(
                            'cat <buildings file name>.csv | grep -v house | grep ",0$"'
                        )
                        sys.exit()

                n.append(list(e.locations[l][nearest_loc_index:]))
                ni.append(nearest_loc_index)

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
