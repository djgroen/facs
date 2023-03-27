import argparse
import csv
import sys
from datetime import datetime, timedelta
from os import makedirs, path
from pprint import pprint

import numpy as np

import facs.base.facs as facs
import facs.base.measures as measures
from facs.readers import (
    read_age_csv,
    read_building_csv,
    read_cases_csv,
    read_disease_yml,
)

if __name__ == "__main__":
    # Instantiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--location", action="store", default="brent")
    parser.add_argument(
        "--ci_multiplier",
        action="store",
        type=float,
        default="0.625",
        help="Multiplier set for Case Isolation which represents the ratio of out-of-house interactions for Covid patients relative to the default interaction rate. Default value comes from Imp Report 9.",
    )
    parser.add_argument("--output_dir", action="store", default=".")
    parser.add_argument("--data_dir", action="store", default="covid_data")
    parser.add_argument(
        "--dbg", action="store_true", help="Write additional outputs to help debugging"
    )
    args = parser.parse_args()
    print(args)

    house_ratio = 2
    location = args.location
    ci_multiplier = float(args.ci_multiplier)
    output_dir = args.output_dir
    data_dir = args.data_dir

    transition_day = -1

    if not path.exists(output_dir):
        makedirs(output_dir)

    end_time = 1100

    print("Running basic Covid-19 simulation kernel.")
    print("scenario = %s" % (location))

    e = facs.Ecosystem(end_time)

    e.ci_multiplier = ci_multiplier
    e.ages = read_age_csv.read_age_csv("{}/age-distr.csv".format(data_dir), location)

    print("age distribution in system:", e.ages, file=sys.stderr)

    e.disease = read_disease_yml.read_disease_yml(
        "{}/disease_covid19.yml".format(data_dir)
    )

    building_file = "{}/{}_buildings.csv".format(data_dir, location)
    read_building_csv.read_building_csv(
        e,
        building_file,
        "{}/building_types_map.yml".format(data_dir),
        house_ratio=house_ratio,
        workspace=12,
        office_size=1600,
        household_size=2.6,
        work_participation_rate=0.5,
        dumpnearest=True,
    )

    print("Nearest locations dump complete.", file=sys.stderr)
