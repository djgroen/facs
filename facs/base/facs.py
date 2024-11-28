"""Main module for the FACS package."""


# FLu And Coronavirus Simulator
# Covid-19 model, based on the general Flee paradigm.

import csv
import random
import sys

from datetime import timedelta

import numpy as np
import pandas as pd

from .needs import Needs
from .location_types import building_types_dict, building_types
from .house import House
from .location import Location
from .utils import (
    probability,
    get_random_int,
    out_files,
    calc_dist,
    write_log_headers,
    check_vac_eligibility,
)
from .mpi import MPIManager

log_prefix = "."

# Global storage for needs now, to keep it simple.
needs = Needs("covid_data/needs.csv", building_types)


class Ecosystem:
    def __init__(self, duration, needsfile="covid_data/needs.csv", mode="parallel"):
        self.mode = mode  # "serial" or "parallel"
        self.locations = {}
        self.houses = []
        self.house_names = []
        self.time = 0
        self.date = None
        self.seasonal_effect = 1.0  # multiplies infection rate due to seasonal effect.
        self.num_hospitalised = 0  # currently in hospital (ICU)
        self.disease = None
        self.closures = {}
        self.validation = np.zeros(duration + 1)
        self.contact_rate_multiplier = {}
        self.initialise_social_distance()  # default: no social distancing.
        self.self_isolation_multiplier = 1.0
        self.household_isolation_multiplier = 1.0
        self.track_trace_multiplier = 1.0
        self.keyworker_fraction = 0.2
        self.ci_multiplier = 0.625  # default multiplier for case isolation mode
        # value is 75% reduction in social contacts for 50% of the cases (known lower compliance).
        # 0.25*50% + 1.0*50% =0.625
        # source: https://www.gov.uk/government/publications/spi-b-key-behavioural-issues-relevant-to-test-trace-track-and-isolate-summary-6-may-2020
        # old default value is derived from Imp Report 9.
        # 75% reduction in social contacts for 70 percent of the cases.
        # (0.25*0.7)+0.3=0.475
        self.num_agents = 0
        self.household_size = 0

        self.work_from_home = False
        self.ages = np.ones(91)  # by default equal probability of all ages 0 to 90.
        self.hospital_protection_factor = 0.2  # 0 is perfect, 1 is no protection.
        self.vaccinations_available = 0  # vaccinations available per day
        self.vaccinations_today = 0
        self.vac_no_symptoms = (
            1.0  # Default: 100% of people receiving vaccine have no more symptons.
        )
        self.vac_no_transmission = 1.0  # Default: 100% of people receiving vaccine transmit the disease as normal.
        self.vaccinations_age_limit = (
            70  # Age limit for priority group. Can be changed at runtime.
        )
        self.vaccinations_legal_age_limit = 16  # Minimum age to be allowed vaccines.
        self.vaccine_effect_time = 14
        self.traffic_multiplier = 0.0
        self.status = {
            "susceptible": 0,
            "exposed": 0,
            "infectious": 0,
            "recovered": 0,
            "dead": 0,
            "immune": 0,
        }
        self.enforce_masks_on_transport = False
        self.loc_groups = {}
        self.needsfile = needsfile

        self.airflow_indoors = 0.007
        self.airflow_outdoors = 0.028  # assuming x4: x20 from the literature but also that people occupy only 20% of the park space on average

        self.external_travel_multiplier = 1.0  # Can be adjusted to introduce peaks in external travel, e.g. during holiday returns or major events (Euros).
        self.external_infection_ratio = 0.5  # May be changed at runtime. Base assumption is that there are 300% extra external visitors, and that 1% of them have COVID. Only applies to transport for now.
        # The external visitor ratio is inflated for now to also reflect external visitors in other settings (which could be implemented later).

        # Settings
        self.immunity_duration = -1  # value > 0 indicates non-permanent immunity.
        self.vac_duration = -1  # value > 0 indicates non-permanent vaccine efficacy.

        # Tracking variables
        self.visit_minutes = 0.0
        self.base_rate = 0.0
        self.loc_evolves = 0.0
        self.number_of_non_house_locations = 0

        self.num_infections_today = 0
        self.num_recoveries_today = 0
        self.num_hospitalisations_today = 0
        self.num_deaths_today = 0

        self.size = 1  # number of processes
        self.rank = 0  # rank of current process
        self.debug_mode = False
        self.verbose = False
        if self.mode == "parallel":
            self.mpi = MPIManager()
            self.rank = (
                self.mpi.comm.Get_rank()
            )  # this is stored outside of the MPI manager, to have one code for seq and parallel.
            self.size = (
                self.mpi.comm.Get_size()
            )  # this is stored outside of the MPI manager, to have one code for seq and parallel.
            self.global_stats = np.zeros(6, dtype="int64")

            print("Hello from process {} out of {}".format(self.rank, self.size))

    def get_partition_size(self, num):
        """
        get process-specific partition of a number.
        """
        part = int(num / self.size)
        if num % self.size > self.rank:
            part += 1
        return part

    def init_loc_inf_minutes(self):
        offset = 0
        self.loc_offsets = {}
        self.loc_m2 = {}
        for lt in self.locations:
            if lt != "house":
                self.loc_m2[lt] = 0.0
                for i in range(0, len(self.locations[lt])):
                    self.locations[lt][i].loc_inf_minutes_id = offset + i
                    self.loc_m2[lt] += self.locations[lt][i].sqm

                if self.rank == 0 and self.verbose:
                    print(
                        "type {}, # {}, tot m2 {}, offset {}".format(
                            lt, len(self.locations[lt]), self.loc_m2[lt], offset
                        )
                    )
                self.number_of_non_house_locations += len(self.locations[lt])
                self.loc_offsets[lt] = offset
                offset += len(self.locations[lt])
        self.loc_inf_minutes = np.zeros(self.number_of_non_house_locations, dtype="f8")

    def reset_loc_inf_minutes(self):
        self.loc_inf_minutes = np.zeros(self.number_of_non_house_locations, dtype="f8")

    def get_date_string(self, date_format="%-d/%-m/%Y"):
        """
        Return the simulation date as a short string.
        """
        return self.date.strftime(date_format)

    def get_seasonal_effect(self):
        month = int(self.date.month)
        multipliers = [1.4, 1.25, 1.1, 0.95, 0.8, 0.7, 0.7, 0.8, 0.95, 1.1, 1.25, 1.4]
        # multipliers = [1.1,1.1,1.05,1.0,1.0,0.95,0.9,0.9,0.95,1.0,1.0,1.05]
        # print("Seasonal effect month: ",month,", multiplier: ",multipliers[month])
        return multipliers[month - 1]

    def make_group(self, loc_type, max_groups):
        """
        Creates a grouping for a location, and assigns agents randomly to groups.
        Agents need to have been read in *before* running this function.
        """
        print("make group:", self.locations.keys(), loc_type)
        num_locs = len(self.locations[loc_type])
        self.loc_groups[loc_type] = {}
        # Assign groups to specific locations of that type in round robin fashion.
        for i in range(0, max_groups):
            self.loc_groups[loc_type][i] = self.locations[loc_type][i % num_locs]

        # randomly assign agents to groups
        for k, e in enumerate(self.houses):
            for hh in e.households:
                for a in hh.agents:
                    a.assign_group(loc_type, max_groups)

    def get_location_by_group(self, loc_type_id, group_num):
        loc_type = building_types[loc_type_id]
        return self.loc_groups[loc_type][group_num]

    def print_contact_rate(self, measure):
        print("Enacted measure:", measure)
        print("contact rate multipliers set to:")
        print(self.contact_rate_multiplier)

    def print_isolation_rate(self, measure):
        print("Enacted measure:", measure)
        print("isolation rate multipliers set to:")
        print(self.self_isolation_multiplier)

    def evolve_public_transport(self):
        """
        Pinf =
        Contact rate multiplier [dimensionless] (Term 1)
        *
        Infection rate [dimensionless] / airflow coefficient [dimensionless] (Term 2)
        *
        Duration of susceptible person visit [minutes] / 1 day [minutes] (Term 3)
        *
        (Average number of infectious person visiting today [#] * physical area of a single standing person [m^2]) /
        (Area of space [m^2]) (Term 4)
        *
        Average infectious person visit duration [minutes] / minutes_opened [minutes] (Term 5)

        """

        if self.time < 0:  # do not model transport during warmup phase!
            return

        self.print_status(None, silent=True)  # Synchronize global stats
        num_agents = (
            self.global_stats[0]
            + self.global_stats[1]
            + self.global_stats[2]
            + self.global_stats[3]
            + self.global_stats[5]
        )  # leaving out [4] because dead people don't travel.
        infected_external_passengers = (
            num_agents * self.external_infection_ratio * self.external_travel_multiplier
        )

        infection_probability = (
            self.traffic_multiplier
        )  # we use travel uptake rate as contact rate multiplier (it implicity has case isolation multiplier in it)
        if self.enforce_masks_on_transport:
            infection_probability *= 0.44  # 56% reduction when masks are widely used: https://www.medrxiv.org/content/10.1101/2020.04.17.20069567v4.full.pdf
        # print(infection_probability)
        infection_probability *= (
            self.disease.infection_rate
        )  # Term 2: Airflow coefficient set to 1, as setting mimics confined spaces from infection rate literature (prison, cruiseship).
        # print(infection_probability)
        infection_probability *= (
            30.0 / 1440.0
        )  # Term 3: visit duration assumed to be 30 minutes per day on average / length of full day.
        # print(infection_probability)
        infection_probability *= (
            (self.global_stats[2] + infected_external_passengers) * 1.0 / num_agents
        )  # Term 4, space available is equal to number of agents.
        # print(infection_probability)
        infection_probability *= (
            30.0 / 900.0
        )  # visit duration assumed to be 30 minutes per day / transport services assumed to be operational for 15 hours per day.

        # print(self.global_stats[2], num_agents, infected_external_passengers, infection_probability)
        # sys.exit()

        # assume average of 40-50 minutes travel per day per travelling person (5 million people travel, so I reduced it to 30 minutes per person), transport open of 900 minutes/day (15h), self_isolation further reduces use of transport, and each agent has 1 m^2 of space in public transport.
        # traffic multiplier = relative reduction in travel minutes^2 / relative reduction service minutes
        # 1. if half the people use a service that has halved intervals, then the number of infection halves.
        # 2. if half the people use a service that has normal intervals, then the number of infections reduces by 75%.

        num_inf = 0
        for i in range(0, len(self.houses)):
            h = self.houses[i]
            for hh in h.households:
                for a in hh.agents:
                    if probability(infection_probability):
                        a.infect(self, location_type="traffic")
                        num_inf += 1

        print(
            "Transport: t {} p_inf {}, inf_ext_pas {}, # of infections {}.".format(
                self.time, infection_probability, infected_external_passengers, num_inf
            )
        )

    def load_nearest_from_file(self, fname):
        """
        Load nearest locations from CSV file.
        """
        try:
            f = open(fname, "r")
            near_reader = csv.reader(f)
            i = 0

            header_row = next(near_reader)
            # print(header_row)
            # print(building_types)
            # sys.exit()

            for row in near_reader:
                # print(row)
                self.houses[i].nearest_locations = row
                n = []
                for j in range(0, len(header_row)):
                    try:
                        n.append(self.locations[header_row[j]][int(row[j])])
                    except:
                        print("ERROR: nearest building lookup from file failed:")
                        print("row in CSV: ", i)
                        print("building_types index: ", j, " len:", len(header_row))
                        print(
                            "self.locations [key][]: ",
                            header_row[j],
                            " [][index]",
                            int(row[j]),
                        )
                        print(
                            "self.locations [keys][]",
                            self.locations.keys(),
                            " [][len]",
                            len(self.locations[header_row[j]]),
                        )
                        sys.exit()
                self.houses[i].nearest_locations = n
                # print(self.houses[i].nearest_locations)
                i += 1
        except IOError:
            return False

    def update_nearest_locations(self, dump_and_exit=False):
        f = None
        read_from_file = False
        if dump_and_exit == True:
            f = open("nearest_locations.csv", "w")

        if dump_and_exit == True:
            # print header row
            print(",".join(f"{x}" for x in building_types), file=f)

        count = 0
        print("Updating nearest locations...", file=sys.stderr)
        for h in self.houses:
            ni = h.find_nearest_locations(self)
            if dump_and_exit == True:
                print(",".join(f"{x}" for x in ni), file=f)
            count += 1
            if count % 1000 == 0:
                print(f"{count} houses scanned.", file=sys.stderr, end="\r")
        print(f"Total {count} houses scanned.", file=sys.stderr)

        print(dump_and_exit)

        if dump_and_exit == True:
            sys.exit()

        if self.mode == "parallel":
            # Assign houses to ranks for parallelisation.

            # count: the size of each sub-task
            ave, res = divmod(len(self.houses), self.size)
            counts = [ave + 1 if p < res else ave for p in range(self.size)]
            self.house_slice_sizes = np.array(counts)

            # offset: the starting index of each sub-task
            offsets = [sum(counts[:p]) for p in range(self.size)]
            self.house_slice_offsets = np.array(offsets)

    def add_infections(self, num, severity="exposed"):
        """
        Randomly add infections.
        """
        # if num > 0:
        if self.verbose:
            print("new infections: ", self.rank, num, self.get_partition_size(num))
        #  sys.exit()
        for i in range(0, self.get_partition_size(num)):
            infected = False
            attempts = 0
            while infected == False and attempts < 500:
                house = int(get_random_int(len(self.houses)))
                infected = self.houses[house].add_infection(self, severity)
                attempts += 1
            if attempts > 499:
                print("WARNING: unable to seed infection.")
        if self.verbose:
            print("add_infections:", num, self.time)

    def add_infection(self, x, y, age):
        """
        Add an infection to the nearest person of that age.
        TODO: stabilize (see function above)
        """
        if age > 90:  # to match demographic data
            age = 90

        selected_house = None
        min_dist = 99999
        if self.verbose:
            print("add_infection:", x, y, age, len(self.houses))

        for h in self.houses:
            dist_h = calc_dist(h.x, h.y, x, y)
            if dist_h < min_dist:
                if h.has_age_susceptible(age):
                    selected_house = h
                    min_dist = dist_h

        # Make sure that cases that are likely recovered
        # already are not included.
        # if day < -self.disease.recovery_period:
        #  day = -int(self.disease.recovery_period)

        selected_house.add_infection_by_age(self, age)

    def _aggregate_loc_inf_minutes(self):
        if self.mode == "parallel":
            # print("loc inf min local: ", self.mpi.rank, self.loc_inf_minutes, type(self.loc_inf_minutes[0]))
            self.loc_inf_minutes = self.mpi.CalcCommWorldTotalDouble(
                self.loc_inf_minutes
            )
        # print("loc inf min:", self.loc_inf_minutes, type(self.loc_inf_minutes[0]))

    def _get_house_rank(self, i):
        rank = -1
        while i >= self.house_slice_offsets[i]:
            rank += 1
        return rank

    def evolve(self, reduce_stochasticity=False):
        self.num_infections_today = 0
        self.num_hospitalisations_today = 0
        self.vaccinations_today = 0

        if self.mode == "parallel" and reduce_stochasticity == True:
            reduce_stochasticity = False
            if self.rank == 0:
                print(
                    "WARNING: reduce stochasticity does not work reliably in parallel mode. It is therefore set to FALSE."
                )

        # remove visits from the previous day
        total_visits = 0

        if self.debug_mode:
            self.visit_minutes = self.mpi.CalcCommWorldTotalSingle(self.visit_minutes)
            self.base_rate = (
                self.mpi.CalcCommWorldTotalSingle(self.base_rate) / self.mpi.size
            )
            self.loc_evolves = self.mpi.CalcCommWorldTotalSingle(self.loc_evolves)

            if self.mpi.rank == 0 and self.verbose:
                print(
                    self.mpi.size,
                    self.time,
                    "total_inf_minutes",
                    np.sum(self.loc_inf_minutes),
                    sep=",",
                )
                print(
                    self.mpi.size, self.time, "total_visit_minutes", self.visit_minutes
                )
                print(self.mpi.size, self.time, "base_rate", self.base_rate)
                print(self.mpi.size, self.time, "loc_evolves", self.loc_evolves)

            self.visit_minutes = 0.0
            self.base_rate = 0.0
            self.loc_evolves = 0.0

        for lk in self.locations.keys():
            for l in self.locations[lk]:
                total_visits += len(l.visits)
                l.clear_visits(self)
        self.reset_loc_inf_minutes()

        if self.rank == 0 and self.verbose:
            print("total visits:", total_visits)

        # collect visits for the current day
        for i in range(0, len(self.houses)):
            h = self.houses[i]
            for hh in h.households:
                for a in hh.agents:
                    a.plan_visits(self)
                    a.progress_condition(self, self.time, self.disease)

                    if (
                        a.age > self.vaccinations_age_limit
                        and self.vaccinations_available - self.vaccinations_today > 0
                    ):
                        if check_vac_eligibility(a) == True:
                            a.vaccinate(
                                self.time,
                                self.vac_no_symptoms,
                                self.vac_no_transmission,
                                self.vac_duration,
                            )
                            self.vaccinations_today += 1

        if self.vaccinations_available - self.vaccinations_today > 0:
            for i in range(0, len(self.houses)):
                h = self.houses[i]
                for hh in h.households:
                    for a in hh.agents:
                        # print("VAC:",self.vaccinations_available, self.vaccinations_today, self.vac_no_symptoms, self.vac_no_transmission, file=sys.stderr)
                        if self.vaccinations_available - self.vaccinations_today > 0:
                            if (
                                a.age > self.vaccinations_legal_age_limit
                                and check_vac_eligibility(a) == True
                            ):
                                a.vaccinate(
                                    self.time,
                                    self.vac_no_symptoms,
                                    self.vac_no_transmission,
                                    self.vac_duration,
                                )
                                self.vaccinations_today += 1

        self._aggregate_loc_inf_minutes()
        if self.rank == 0 and self.verbose:
            print(self.rank, np.sum(self.loc_inf_minutes))

        # process visits for the current day (spread infection).
        for lk in self.locations:
            if lk in self.closures:
                if self.closures[lk] < self.time:
                    continue
            for l in self.locations[lk]:
                l.evolve(self, reduce_stochasticity)

        # process intra-household infection spread.
        for i in range(0, len(self.houses)):
            h = self.houses[i]
            h.evolve(self, self.disease)

        # process infection via public transport.
        self.evolve_public_transport()

        self.time += 1
        self.date = self.date + timedelta(days=1)
        self.seasonal_effect = self.get_seasonal_effect()

    def addHouse(self, name, x, y, num_households=1):
        house = House(x, y)
        house.add_households(self.household_size, self.ages, num_households)
        self.num_agents += house.total_size
        self.houses.append(house)

        self.house_names.append(name)
        return house

    def addRandomOffice(self, office_log, name, xbounds, ybounds, office_size):
        """
        Office coords are generated on proc 0, then broadcasted to others.
        """

        data = None
        if self.mpi.rank == 0:
            x = random.uniform(xbounds[0], xbounds[1])
            y = random.uniform(ybounds[0], ybounds[1])
            data = [x, y]

        data = self.mpi.comm.bcast(data, root=0)
        # print("Coords: ",self.mpi.rank, data)
        self.addLocation(name, "office", data[0], data[1], office_size)
        office_log.write("office,{},{},{}\n".format(data[0], data[1], office_size))

    def addLocation(self, name, loc_type, x, y, sqm=400):
        l = Location(name, loc_type, x, y, sqm)
        if loc_type in self.locations.keys():
            self.locations[loc_type].append(l)
        else:
            self.locations[loc_type] = [l]
        return l

    def add_closure(self, loc_type, time):
        self.closures[loc_type] = time

    def remove_closure(self, loc_type):
        del self.closures[loc_type]

    def remove_closures(self):
        self.closures = {}

    def add_partial_closure(self, loc_type, fraction=0.8, exclude_people=False):
        if loc_type == "school":
            fraction = min(fraction, 1.0 - self.keyworker_fraction)
            if exclude_people:
                for k, e in enumerate(self.houses):
                    for hh in e.households:
                        for a in hh.agents:
                            if probability(fraction):
                                a.school_from_home = True
                            else:
                                a.school_from_home = False
            else:
                needs.scale_needs(loc_type, 1.0 - fraction)

        elif loc_type == "office":
            fraction = min(fraction, 1.0 - self.keyworker_fraction)
            if exclude_people:
                for k, e in enumerate(self.houses):
                    for hh in e.households:
                        for a in hh.agents:
                            if probability(fraction):
                                a.work_from_home = True
                            else:
                                a.work_from_home = False
            else:
                needs.scale_needs(loc_type, 1.0 - fraction)

        else:
            if loc_type == "school_parttime":
                loc_type = "school"

            needs.scale_needs(loc_type, 1.0 - fraction)

    def undo_partial_closure(self, loc_type, fraction=0.8):
        if loc_type == "school":
            for k, e in enumerate(self.houses):
                for hh in e.households:
                    for a in hh.agents:
                        a.school_from_home = False
        elif loc_type == "office":
            for k, e in enumerate(self.houses):
                for hh in e.households:
                    for a in hh.agents:
                        a.work_from_home = False
        else:
            needs.scale_needs(loc_type, 1.0 / (1.0 - fraction))

    def initialise_social_distance(self, contact_ratio=1.0):
        for l in building_types_dict:
            self.contact_rate_multiplier[l] = contact_ratio
        self.contact_rate_multiplier["house"] = 1.0
        self.print_contact_rate("Reset to no measures")

    def reset_case_isolation(self):
        self.self_isolation_multiplier = 1.0
        self.print_isolation_rate(
            "Removing CI, now multiplier is {}".format(self.self_isolation_multiplier)
        )

    def remove_social_distance(self):
        self.initialise_social_distance()
        if self.work_from_home:
            self.add_work_from_home(self.work_from_home_compliance)
        self.print_contact_rate("Removal of SD")

    def remove_all_measures(self):
        global needs
        self.initialise_social_distance()
        self.remove_closures()
        needs = Needs(self.needsfile, building_types)
        for k, e in enumerate(self.houses):
            for hh in e.households:
                for a in hh.agents:
                    a.school_from_home = False
                    a.work_from_home = False

    def add_work_from_home(self, compliance=0.75):
        self.add_partial_closure("office", compliance, exclude_people=True)
        self.print_contact_rate("Work from home with {} compliance".format(compliance))

    def add_social_distance(
        self, distance=2.0, compliance=0.8571, mask_uptake=0.0, mask_uptake_shopping=0.0
    ):
        distance += (
            mask_uptake * 1.0
        )  # if everyone wears a mask, we add 1.0 meter to the distancing,
        tight_distance = 1.0 + mask_uptake_shopping * 1.0
        # representing a ~75% reduction for a base distance of 1 m, and a ~55% reduction for a base distance of 2 m.
        # Source: https://www.medrxiv.org/content/10.1101/2020.04.17.20069567v4.full.pdf

        dist_factor = (0.8 / distance) ** 2
        dist_factor_tight = (
            0.8 / tight_distance
        ) ** 2  # assuming people stay 1 meter apart in tight areas
        # 0.5 is seen as a rough border between intimate and interpersonal contact,
        # based on proxemics (Edward T Hall).
        # But we'll take 0.8 as a standard average interpersonal distance.
        # The -2 exponent is based on the observation that particles move linearly in
        # one dimension, and diffuse in the two other dimensions.
        # gravitational effects are ignored, as particles on surfaces could still
        # lead to future contamination through surface contact.

        # dist_factor_tight excludes mask wearing, as this is incorporated explicitly for supermarkets and shopping.

        for k, e in enumerate(self.contact_rate_multiplier):
            if e in ["supermarket", "shopping"]:  # 2M not practical, so we use 1M+.
                m = dist_factor_tight * compliance + (1.0 - compliance)
            if (
                e in "house"
            ):  # Intra-household interactions are boosted when there is SD outside (Imp Report 9)
                m = 1.25
            else:  # Default is 2M social distancing.
                m = dist_factor * compliance + (1.0 - compliance)

            self.contact_rate_multiplier[e] *= m

        self.print_contact_rate(
            "SD (covid_flee method) with distance {} and compliance {}".format(
                distance, compliance
            )
        )

    def add_case_isolation(self):
        self.self_isolation_multiplier = (
            self.ci_multiplier * self.track_trace_multiplier
        )
        self.print_isolation_rate(
            "CI with multiplier {}".format(self.self_isolation_multiplier)
        )

    def reset_household_isolation(self):
        self.household_isolation_multiplier = 1.0
        self.print_isolation_rate(
            "Household isolation with multiplier {}".format(
                self.self_isolation_multiplier
            )
        )

    def add_household_isolation(self, multiplier=0.625):
        # compulsory household isolation
        # assumption: 50% of household members complying
        # 25%*50% + 100%*50% = 0.625
        # source: https://www.gov.uk/government/publications/spi-b-key-behavioural-issues-relevant-to-test-trace-track-and-isolate-summary-6-may-2020
        # old assumption: a reduction in contacts by 75%, and
        # 80% of household complying. (Imp Report 9)
        # 25%*80% + 100%*20% = 40% = 0.4
        self.household_isolation_multiplier = multiplier
        self.print_isolation_rate(
            "Household isolation with {} multiplier".format(multiplier)
        )

    def add_cum_column(self, csv_file, cum_columns):
        if self.rank == 0:
            df = pd.read_csv(csv_file, index_col=None, header=0)

            for column in cum_columns:
                df["cum %s" % (column)] = df[column].cumsum()

            df.to_csv(csv_file, index=False)

    def find_hospital(self):
        hospitals = []
        sqms = []
        if "hospital" not in self.locations.keys():
            print("Error: couldn't find hospitals with more than 4000 sqm.")
            sys.exit()
        else:
            for k, element in enumerate(
                self.locations["hospital"]
            ):  # using 'element' to avoid clash with Ecosystem e.
                if element.sqm > 4000:
                    sqms += [element.sqm]
                    hospitals += [self.locations["hospital"][k]]
            if len(hospitals) == 0:
                print("Error: couldn't find hospitals with more than 4000 sqm.")
                sys.exit()
        sqms = [float(i) / sum(sqms) for i in sqms]
        return np.random.choice(hospitals, p=sqms)

    def print_needs(self):
        for k, e in enumerate(self.houses):
            for hh in e.households:
                for a in hh.agents:
                    print(k, a.get_needs())

    def print_header(self, outfile):
        write_log_headers(
            self.rank
        )  # also write headers for process-specific log files.
        if self.rank == 0:
            out = out_files.open(outfile)
            print(
                "#time,date,susceptible,exposed,infectious,recovered,dead,immune,num infections today,num hospitalisations today,hospital bed occupancy,num hospitalisations today (data)",
                file=out,
                flush=True,
            )

    def print_status(self, outfile, silent=False):
        local_stats = {
            "susceptible": 0,
            "exposed": 0,
            "infectious": 0,
            "recovered": 0,
            "dead": 0,
            "immune": 0,
            "num_infections_today": self.num_infections_today,
            "num_hospitalisations_today": self.num_hospitalisations_today,
            "num_hospitalised": self.num_hospitalised,
        }
        for k, elem in enumerate(self.houses):
            for hh in elem.households:
                for a in hh.agents:
                    # print(hh,a, a.status)
                    local_stats[a.status] += 1
        self.mpi.gather_stats(self, list(local_stats.values()))
        if not silent:
            if self.rank == 0:
                out = out_files.open(outfile)
                t = max(0, self.time)

                print(
                    self.time,
                    self.get_date_string(),
                    *self.global_stats,
                    self.validation[t],
                    sep=",",
                    file=out,
                    flush=True,
                )

    def dump_locations(self):
        out_inf = out_files.open(
            "{}/locations_{}.csv".format(log_prefix, self.mpi.rank)
        )
        print("#type,x,y,sqm", file=out_inf, flush=True)
        for h in self.houses:
            print("house,{},{},-1".format(h.x, h.y), file=out_inf, flush=True)
        for lt in self.locations:
            for i in range(0, len(self.locations[lt])):
                print(
                    "{},{},{},{}".format(
                        lt,
                        self.locations[lt][i].x,
                        self.locations[lt][i].y,
                        self.locations[lt][i].sqm,
                    ),
                    file=out_inf,
                    flush=True,
                )

    def add_validation_point(self, time):
        self.validation[max(time, 0)] += 1

    def print_validation(self):
        print(self.validation)
        sys.exit()
