from facs.base import facs as facs
from facs.base import measures as measures
from facs.readers import read_age_csv
import numpy as np
from facs.readers import read_building_csv
from facs.readers import read_cases_csv
from facs.readers import read_disease_yml
import sys

from os import makedirs, path
import argparse
import csv
from pprint import pprint

from datetime import datetime, timedelta


if __name__ == "__main__":

    # Instantiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--location', action="store", default="brent", help="Name of location to load.")
    parser.add_argument('-m','--measures_yml', action="store", default="measures_uk", help="Input YML file containing interventions.")
    parser.add_argument('-d','--disease_yml', action="store", default="disease_covid19", help="Input YML file containing disease specification.")
    parser.add_argument('-v','--vaccinations_yml', action="store", default="vaccinations", help="Input YML file containing vaccine strategy specification.")
    parser.add_argument('--output_dir', action="store", default=".", help="directory to write output to.")
    parser.add_argument('--data_dir', action="store", default="covid_data", help="subdirectory containing simulation input data.")
    parser.add_argument('-s','--starting_infections', action="store", default="500", help="Starting # of infections. Values below 1.0 are interpreted as a ratio of population.")
    parser.add_argument('--start_date', action="store", default="1/3/2020", help="Start date, format = %d/%m/%Y")
    parser.add_argument('-q', '--quicktest', action="store_true", help="set house_ratio to 100 to do quicker (but less accurate) runs for populous regions.")
    parser.add_argument('-g', '--generic_outfile', action="store_true", help="Write main output to out.csv instead of a scenario-specific named file.")
    parser.add_argument('--dbg', action="store_true", help="Write additional outputs to help debugging")
    parser.add_argument('-t', '--simulation_period', action="store",type=int, default='-1', help="Simulation duration [days].")
    args = parser.parse_args()
    print(args)

    house_ratio = 2
    if args.quicktest:
      house_ratio = 100
    location = args.location
    measures_yml = args.measures_yml
    disease_yml = args.disease_yml
    vaccinations_yml = args.vaccinations_yml
    output_dir = args.output_dir
    data_dir = args.data_dir

    # if simsetting.csv exists -> overwrite the simulation setting parameters
    if path.isfile('simsetting.csv'):
        with open('simsetting.csv', newline='') as csvfile:
            values = csv.reader(csvfile)
            for row in values:
                if len(row) > 0:  # skip empty lines in csv
                    if row[0][0] == "#":
                        pass
                    elif row[0].lower() == "measures_yml":
                        measures_yml = str(row[1]).lower()

    # check if output_dir is exists
    if not path.exists(output_dir):
        makedirs(output_dir)

    outfile = "{}/{}-{}.csv".format(output_dir,
                                       location,
                                       measures_yml)
    if args.generic_outfile:
      outfile = "{}/out.csv".format(output_dir)

    end_time = 1100
    
    if args.simulation_period > 0:
      end_time = args.simulation_period
    
    print("Running basic Covid-19 simulation kernel.")
    print("scenario = %s" % (location))
    print("measures input yml = %s" % (measures_yml))
    print("disease input yml = %s" % (disease_yml))
    print("vaccinations input yml = %s" % (vaccinations_yml))
    print("end_time = %d" % (end_time))
    print("output_dir  = %s" % (output_dir))
    print("outfile  = %s" % (outfile))
    print("data_dir  = %s" % (data_dir))

    e = facs.Ecosystem(end_time)

    e.ages = read_age_csv.read_age_csv("{}/age-distr.csv".format(data_dir), location)

    print("age distribution in system:", e.ages, file=sys.stderr)

    e.disease = read_disease_yml.read_disease_yml(
        "{}/{}.yml".format(data_dir, disease_yml))

    building_file = "{}/{}_buildings.csv".format(data_dir, location)
    read_building_csv.read_building_csv(e,
                                        building_file,
                                        "{}/building_types_map.yml".format(data_dir),
                                        house_ratio=house_ratio, workspace=20, office_size=2500, household_size=2.6, work_participation_rate=0.5)
    # house ratio: number of households per house placed (higher number adds noise, but reduces runtime
    # And then 3 parameters that ONLY affect office placement.
    # workspace: m2 per employee on average. (10 in an office setting, but we use 20 as some people work in much more spacious environments)
    # household size: average size of each household, specified separately here.
    # work participation rate: fraction of population in workforce, irrespective of age

    #print("{}/{}_cases.csv".format(data_dir, location))
    # Can only be done after houses are in.
    #read_cases_csv.read_cases_csv(e,
    #                              "{}/{}_cases.csv".format(data_dir, location),
    #                              start_date=args.start_date,
    #                              date_format="%m/%d/%Y")

    e.print_status(outfile, silent=True) # silent print to initialise log data structures.

    starting_num_infections = 500
    if args.starting_infections:
        if int(args.starting_infections[0]) == 0:
            starting_num_infections = int(e.num_agents*float(args.starting_infections))
        else:
            starting_num_infections = int(args.starting_infections)
    elif location == "test":
        starting_num_infections = 10

    print("THIS SIMULATIONS HAS {} AGENTS. Starting with {} infections.".format(e.num_agents, starting_num_infections))

    e.time = -20
    e.date = datetime.strptime(args.start_date, "%d/%m/%Y")
    e.date = e.date - timedelta(days=20)
    e.print_header(outfile)
    for i in range(0, 20):
        
        # Roughly evenly spread infections over the days.
        num = int(starting_num_infections/20)
        if starting_num_infections % 20 > i:
          num += 1
        
        e.add_infections(num)

        measures.enact_measures_and_evolutions(e, e.time, measures_yml, vaccinations_yml)
        
        e.evolve(reduce_stochasticity=False)

        print(e.time)
        if args.dbg:
            e.debug_mode = True
            e.print_status(outfile)
        else:
            e.debug_mode = False
            e.print_status(outfile, silent=True)


    for t in range(0, end_time):

        measures.enact_measures_and_evolutions(e, e.time, measures_yml, vaccinations_yml)

        # Propagate the model by one time step.
        e.evolve(reduce_stochasticity=False)

        print(t, e.get_date_string(),  e.vac_no_symptoms, e.vac_no_transmission)
        e.print_status(outfile)

    # calculate cumulative sums.
    e.add_cum_column(outfile, ["num hospitalisations today", "num infections today"])

    print("Simulation complete.", file=sys.stderr)
