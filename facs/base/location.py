"""Module containing the Location class, which represents a location in the simulation."""

import sys

from .location_types import building_types_dict
from .utils import probability


avg_visit_times = [90, 60, 60, 360, 360, 60, 60]  # average time spent per visit


class Location:
    def __init__(self, name, loc_type="park", x=0.0, y=0.0, sqm=400):
        if loc_type not in building_types_dict.keys():
            print(
                "Error: location type {} is not in the recognised lists of location ids (building_types_dict).".format(
                    loc_type
                )
            )
            sys.exit()

        self.name = name
        self.x = x
        self.y = y
        self.links = []  # paths connecting to other locations
        self.closed_links = []  # paths connecting to other locations that are closed.
        self.type = loc_type  # supermarket, park, hospital, shopping, school, office, leisure? (home is a separate class, to conserve memory)
        self.sqm = sqm  # size in square meters.
        self.loc_inf_minutes_id = -1  # id of minutes tracking in global array.

        if loc_type == "park":
            self.sqm *= 10  # https://www.medrxiv.org/content/10.1101/2020.02.28.20029272v2 (I took a factor of 10 instead of 19 due to the large error bars)

        self.visits = []
        # print(loc_type, len(building_types_dict), building_types_dict[loc_type], len(avg_visit_times))
        self.avg_visit_time = avg_visit_times[
            building_types_dict[loc_type]
        ]  # using averages for all visits for now. Can replace with a distribution later.
        # print(self.avg_visit_time)
        self.visit_probability_counter = (
            0.5  # counter used for deterministic calculations.
        )

    def clear_visits(self, e):
        self.visits = []
        e.loc_inf_minutes[self.loc_inf_minutes_id] = 0.0

    def register_visit(self, e, person, need, deterministic):
        visit_time = self.avg_visit_time
        if person.status == "dead":
            return
        elif person.status == "infectious":
            visit_time *= (
                e.self_isolation_multiplier
            )  # implementing case isolation (CI)
            if self.type == "hospital":
                if person.hospitalised:
                    e.loc_inf_minutes[self.loc_inf_minutes_id] += (
                        need / 7 * e.hospital_protection_factor
                    )
                    return

        elif (
            person.household.is_infected()
        ):  # person is in household quarantine, but not subject to CI.
            visit_time *= e.household_isolation_multiplier

        visit_probability = 0.0
        if visit_time > 0.0:
            visit_probability = need / (
                visit_time * 7
            )  # = minutes per week / (average visit time * days in the week)
            # if ultraverbose:
            #  print("visit prob = ", visit_probability)
        else:
            return

        if deterministic:
            self.visit_probability_counter += min(visit_probability, 1)
            if self.visit_probability_counter > 1.0:
                self.visit_probability_counter -= 1.0
                self.visits.append([person, visit_time])
                if person.status == "infectious":
                    e.loc_inf_minutes[self.loc_inf_minutes_id] += visit_time

        elif probability(visit_probability):
            self.visits.append([person, visit_time])
            if person.status == "infectious":
                e.loc_inf_minutes[self.loc_inf_minutes_id] += visit_time

    def evolve(self, e, deterministic=False):
        """
        (i)
        Pinf =
        Contact rate multiplier [dimensionless] * 4 (to correct for a 1m2 baseline, rather than 4 m2.)
        *
        Infection rate [dimensionless] / airflow coefficient [dimensionless]
        *
        Duration of susceptible person visit [minutes] / 1 day [minutes]
        *
        (Number of infectious person visiting today [#] * physical area of a single standing person [m^2]) /
        (Area of space [m^2] * number of infectious persons in 4 m^2 in baseline scenario (1) [#])
        *
        Average infectious person visit duration [minutes] / minutes_opened [minutes]

        Pinf is a dimensionless quantity (a probability) which must never exceed one.

        (ii)
        if we define Pinf = Duration of susceptible person visit [minutes] * base_rate,
        and substitute in the # of infectious people in the baseline scenario (i.e., 1), then we get:
        base_rate =
        Contact rate multiplier [dimensionless] * 4 (to correct for a 1m2 baseline, rather than 4 m2.)
        *
        Infection rate [dimensionless] / airflow coefficient [dimensionless]
        *
        1.0 / 1 day [minutes]
        *
        (Number of infectious person visiting today [#] * physical area of a single standing person [m^2]) /
        (Area of space [m^2])
        *
        Average infectious person visit duration [minutes] / minutes_opened [minutes]

        base_rate has a quantity of [minutes^-1].

        (iii)
        Furthermore, we have a merged quantity infected_minutes:
        infected_minutes = Average number of infectious person visiting today [#] * Average infectious person visit duration [minutes]
        And we define two constants:
        1. physical area of a single standing person [m^2], which we set to 1 m^2.

        So we rewrite base_rate at:
        base_rate =
        Contact rate multiplier [dimensionless] * 4 (to correct for a 1m2 baseline, rather than 4 m2.)
        *
        Infection rate [dimensionless] / airflow coefficient [dimensionless]
        *
        1.0 / 1 day [minutes]
        *
        1 [m^2] /
        (Area of space [m^2])
        *
        Total infectious person minutes [minutes] / minutes_opened [minutes]

        (iv)
        Lastly, we simplify the equation for easier coding to:

        base_rate =
        4.0
        *
        ( Contact rate multiplier [dimensionless]
        *
        Infection rate [dimensionless]
        *
        Total infectious person minutes [minutes] )
        /
        ( airflow coefficient [dimensionless]
        *
        24*60 [minutes]
        *
        Area of space [m^2]
        *
        minutes_opened [minutes] (

        in code this then becomes:
        """

        # supermarket, park, hospital, shopping, school, office, leisure
        minutes_opened = 12 * 60
        airflow = e.airflow_indoors
        if self.type == "park":
            airflow = e.airflow_outdoors

        base_rate = (
            4.0
            * e.seasonal_effect
            * e.contact_rate_multiplier[self.type]
            * e.disease.infection_rate
            * float(e.loc_inf_minutes[self.loc_inf_minutes_id])
        ) / (float(airflow) * 24.0 * 60.0 * float(self.sqm) * float(minutes_opened))

        e.base_rate += base_rate

        # if e.rank == 0:
        #  print("RATES:", base_rate, e.loc_inf_minutes[self.loc_inf_minutes_id], self.loc_inf_minutes_id)

        # dump rates
        # out_inf = out_files.open("{}/rates_{}.csv".format(log_prefix, e.mpi.rank))
        # print(self.type, self.sqm, self.loc_inf_minutes_id, e.loc_inf_minutes[self.loc_inf_minutes_id], base_rate, file=out_inf, flush=True)

        # Deterministic mode: only used for warmup.
        if deterministic:
            print(
                "reduce_stochasticity not supported for the time being, due to instabilities in parallel implementation."
            )
            # sys.exit()
            # inf_counter = 1.0 - (0.5 / float(e.mpi.size))
            # for v in self.visits:
            #  e.loc_evolves += 1
            #  if v[0].status == "susceptible":
            #    infection_probability = v[1] * base_rate
            #    inf_counter += min(infection_probability, 1.0)
            #    if inf_counter > 1.0:
            #      inf_counter -= 1.0
            #      v[0].infect(e, location_type=self.type)

        # Used everywhere else
        else:
            for v in self.visits:
                e.loc_evolves += 1
                if v[0].status == "susceptible":
                    infection_probability = v[1] * base_rate
                    if infection_probability > 0.0:
                        # print("{} = {} * ({}/360.0) * ({}/{}) * ({}/{})".format(infection_probability, e.contact_rate_multiplier[self.type], e.disease.infection_rate, v[1], minutes_opened, e.loc_inf_minutes[self.loc_inf_minutes_id], self.sqm))
                        if probability(infection_probability):
                            v[0].infect(e, location_type=self.type)