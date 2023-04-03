"""Script to run facs"""

import argparse
import csv
import sys
from datetime import datetime, timedelta
from os import makedirs, path

from facs.base import facs
from facs.base import measures
from facs.readers import (
    read_age_csv,
    read_building_csv,
    read_disease_yml,
)


def parse_arguments() -> dict:
    """Formats command-line arguments as dictionary

    Returns:
        dict: Dictionary of all command line arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--location", action="store", default="brent", help="Name of location to load."
    )
    parser.add_argument(
        "-m",
        "--measures_yml",
        action="store",
        default="measures_uk",
        help="Input YML file containing interventions.",
    )
    parser.add_argument(
        "-d",
        "--disease_yml",
        action="store",
        default="disease_covid19",
        help="Input YML file containing disease specification.",
    )
    parser.add_argument(
        "-v",
        "--vaccinations_yml",
        action="store",
        default="vaccinations",
        help="Input YML file containing vaccine strategy specification.",
    )
    parser.add_argument(
        "--output_dir",
        action="store",
        default=".",
        help="directory to write output to.",
    )
    parser.add_argument(
        "--data_dir",
        action="store",
        default="covid_data",
        help="subdirectory containing simulation input data.",
    )
    parser.add_argument(
        "-s",
        "--starting_infections",
        action="store",
        default="500",
        help="Starting # of infections. Values below 1.0 are interpreted as a ratio of population.",
    )
    parser.add_argument(
        "--household_size",
        action="store",
        default="2.6",
        help="Average household size.",
    )
    parser.add_argument(
        "--start_date",
        action="store",
        default="1/3/2020",
        help="Start date, format = %d/%m/%Y",
    )
    parser.add_argument(
        "-q",
        "--quicktest",
        action="store_true",
        help="set house_ratio to 100 to do quicker (but less accurate) runs for populous regions.",
    )
    parser.add_argument(
        "-g",
        "--generic_outfile",
        action="store_true",
        help="Write main output to out.csv instead of a scenario-specific named file.",
    )
    parser.add_argument(
        "--dbg", action="store_true", help="Write additional outputs to help debugging"
    )
    parser.add_argument(
        "-t",
        "--simulation_period",
        action="store",
        type=int,
        default="-1",
        help="Simulation duration [days].",
    )
    parser.add_argument(
        "-o",
        "--office_size",
        action="store",
        type=int,
        default="2500",
        help="Office size in m2.",
    )
    parser.add_argument(
        "-w",
        "--workspace",
        action="store",
        type=int,
        default="20",
        help="Workspace per person in m2.",
    )
    return parser.parse_args()


def get_house_ratio(test: bool) -> float:
    """Returns the number of households in a single house

    Args:
        test (bool): Flag to check if test run

    Returns:
        float: House ratio
    """

    return 100 if test else 2


def get_measures_file(filename: str) -> str:
    """Returns the measures filename from simsettings.csv or the given argument

    Args:
        filename (str): measures filename argument

    Returns:
        str: Measures filename to be used
    """

    # if simsetting.csv exists -> overwrite the simulation setting parameters
    if path.isfile("simsetting.csv"):
        with open("simsetting.csv", newline="", encoding="utf-8") as csvfile:
            values = csv.reader(csvfile)
            for row in values:
                if len(row) > 0:  # skip empty lines in csv
                    if row[0][0] == "#":
                        pass
                    elif row[0].lower() == "measures_yml":
                        return str(row[1]).lower()

    return str(filename)


if __name__ == "__main__":
    args = parse_arguments()

    print(args)

    house_ratio = get_house_ratio(args.quicktest)
    location = args.location
    measures_yml = get_measures_file(args.measures_yml)
    disease_yml = args.disease_yml
    vaccinations_yml = args.vaccinations_yml
    output_dir = args.output_dir
    data_dir = args.data_dir
    household_size = float(args.household_size)
    end_time = args.simulation_period if args.simulation_period > 0 else 1100

    # check if output_dir is exists
    if not path.exists(output_dir):
        makedirs(output_dir)

    outfile = f"{output_dir}/{location}-{measures_yml}.csv"
    if args.generic_outfile:
        outfile = f"{output_dir}/out.csv"

    workspace = args.workspace
    office_size = args.office_size

    print("Running basic Covid-19 simulation kernel.")
    print(f"scenario = {location}")
    print(f"measures input yml = {measures_yml}")
    print(f"disease input yml = {disease_yml}")
    print(f"vaccinations input yml = {vaccinations_yml}")
    print(f"end_time = {end_time}")
    print(f"output_dir  = {output_dir}")
    print(f"outfile  = {outfile}")
    print(f"data_dir  = {data_dir}")

    e = facs.Ecosystem(end_time)

    e.ages = read_age_csv.read_age_csv(f"{data_dir}/age-distr.csv", location)

    print("age distribution in system:", e.ages, file=sys.stderr)

    e.disease = read_disease_yml.read_disease_yml(f"{data_dir}/{disease_yml}.yml")

    building_file = f"{data_dir}/{location}_buildings.csv"
    read_building_csv.read_building_csv(
        e,
        building_file,
        f"{data_dir}/building_types_map.yml",
        house_ratio=house_ratio,
        workspace=workspace,
        office_size=office_size,
        household_size=household_size,
        work_participation_rate=0.5,
    )
    # house ratio: number of households per house placed (higher number adds noise, but reduces
    # runtime
    # And then 3 parameters that ONLY affect office placement.
    # workspace: m2 per employee on average. (10 in an office setting, but we use 20 as some
    # people work in much more spacious environments)
    # household size: average size of each household, specified separately here.
    # work participation rate: fraction of population in workforce, irrespective of age

    # print("{}/{}_cases.csv".format(data_dir, location))
    # Can only be done after houses are in.
    # read_cases_csv.read_cases_csv(e,
    #                              "{}/{}_cases.csv".format(data_dir, location),
    #                              start_date=args.start_date,
    #                              date_format="%m/%d/%Y")

    e.print_status(
        outfile, silent=True
    )  # silent print to initialise log data structures.

    starting_num_infections = 500
    if args.starting_infections:
        if int(args.starting_infections[0]) == 0:
            # Aggregate the num agents before using the starting infections multiplier.
            num_agents_all = e.mpi.CalcCommWorldTotalSingle(float(e.num_agents))
            print("Num agents all:", num_agents_all)
            starting_num_infections = int(
                (num_agents_all * float(args.starting_infections))
            )
        else:
            starting_num_infections = int(args.starting_infections)
    elif location == "test":
        starting_num_infections = 10

    print(
        f"THIS SIMULATIONS HAS {e.num_agents} AGENTS."
        f"Starting with {starting_num_infections} infections."
    )

    e.time = -20
    e.date = datetime.strptime(args.start_date, "%d/%m/%Y")
    e.date = e.date - timedelta(days=20)
    e.print_header(outfile)
    for i in range(0, 20):
        # Roughly evenly spread infections over the days.
        num = int(starting_num_infections / 20)
        if starting_num_infections % 20 > i:
            num += 1

        e.add_infections(num)

        measures.enact_measures_and_evolutions(
            e, e.time, measures_yml, vaccinations_yml, disease_yml
        )

        e.evolve(reduce_stochasticity=False)

        print(e.time)
        if args.dbg:
            e.debug_mode = True
            e.print_status(outfile)
        else:
            e.debug_mode = False
            e.print_status(outfile, silent=True)

    for t in range(0, end_time):
        measures.enact_measures_and_evolutions(
            e, e.time, measures_yml, vaccinations_yml, disease_yml
        )

        # Propagate the model by one time step.
        e.evolve(reduce_stochasticity=False)

        print(t, e.get_date_string(), e.vac_no_symptoms, e.vac_no_transmission)
        e.print_status(outfile)

    # calculate cumulative sums.
    e.add_cum_column(outfile, ["num hospitalisations today", "num infections today"])

    print("Simulation complete.", file=sys.stderr)
