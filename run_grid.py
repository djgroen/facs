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

    # Instantiate the parameters
    location = sys.argv[1]
    measures_yml = sys.argv[2]
    disease_yml = sys.argv[3]
    vaccinations_yml = sys.argv[4]
    output_dir = sys.argv[5]
    data_dir = sys.argv[6]
    starting_infections = sys.argv[7]
    start_date = sys.argv[8]
    quicktest = int(sys.argv[9])
    generic_outfile = int(sys.argv[10])
    dbg = int(sys.argv[11])
    simulation_period = int(sys.argv[12])
    print(str(sys.argv))

    house_ratio = 2
    if quicktest == 1:
      house_ratio = 100

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

    # creating directory specific to the location
    facs.log_prefix = "{}_logs_dir".format(location)

    # check if logs_dir is exists
    if not path.exists(facs.log_prefix):
        makedirs(facs.log_prefix)

    # check if output_dir is exists
    if not path.exists(output_dir):
        makedirs(output_dir)

    outfile = "{}/{}-{}.csv".format(output_dir,
                                       location,
                                       measures_yml)
    if generic_outfile == 1:
      outfile = "{}/out.csv".format(output_dir)

    end_time = 1100
    
    if simulation_period > 0:
      end_time = simulation_period
    
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
    #                              start_date=start_date,
    #                              date_format="%m/%d/%Y")

    e.print_status(outfile, silent=True) # silent print to initialise log data structures.

    starting_num_infections = 500
    if starting_infections != 500:
        if int(starting_infections[0]) == 0:
            # Aggregate the num agents before using the starting infections multiplier.
            num_agents_all = e.mpi.CalcCommWorldTotalSingle(float(e.num_agents))
            print("Num agents all:",num_agents_all)
            starting_num_infections = int((num_agents_all*float(starting_infections)))
        else:
            starting_num_infections = int(starting_infections)
    elif location == "test":
        starting_num_infections = 10

    print("THIS SIMULATIONS HAS {} AGENTS. Starting with {} infections.".format(e.num_agents, starting_num_infections))

    e.time = -20
    e.date = datetime.strptime(start_date, "%d/%m/%Y")
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
        if dbg == 1:
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
