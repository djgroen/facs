"""Module for the House class."""


import sys

import numpy as np

from .household import Household
from .utils import get_random_int, calc_dist
from .location_types import building_types


class House:
    def __init__(self, e, x, y, num_households=1):
        self.x = x
        self.y = y
        self.households = []
        self.num_agents = 0
        for i in range(0, num_households):
            size = 1 + np.random.poisson(e.household_size - 1)
            e.num_agents += size
            self.households.append(Household(self, e.ages, size))

    def IncrementNumAgents(self):
        self.num_agents += 1

    def DecrementNumAgents(self):
        self.num_agents -= 1

    def evolve(self, e, time, disease):
        for hh in self.households:
            hh.evolve(e, disease)

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
                        d = calc_dist(self.x, self.y, element.x, element.y) / np.sqrt(
                            element.sqm
                        )
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

                n.append(e.locations[l][nearest_loc_index])
                ni.append(nearest_loc_index)

        # for i in n:
        #  if i:
        #    print(i.name, i.type)
        self.nearest_locations = n
        return ni

    def add_infection(
        self, e, severity="exposed"
    ):  # used to preseed infections (could target using age later on)
        hh = int(get_random_int(len(self.households)))
        p = get_random_int(len(self.households[hh].agents))
        if self.households[hh].agents[p].status == "susceptible":
            # because we do pre-seeding we need to ensure we add exactly 1 infection.
            self.households[hh].agents[p].infect(e, severity)
            infection_pending = False
            return True
        return False

    def has_age(self, age):
        for hh in self.households:
            for a in hh.agents:
                if a.age == age:
                    if a.status == "susceptible":
                        return True
        return False

    def add_infection_by_age(self, e, age):
        for hh in self.households:
            for a in hh.agents:
                if a.age == age:
                    if a.status == "susceptible":
                        a.infect(e, severity="exposed")
