import facs.facs as facs
import facs.measures as measures
from readers import read_age_csv
import numpy as np
from readers import read_building_csv
from readers import read_cases_csv
from readers import read_disease_yml
import sys

from os import makedirs, path
import argparse
import csv
from pprint import pprint


if __name__ == "__main__":

    # Instantiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--location', action="store", default="brunel")
    parser.add_argument('--transition_scenario', action="store", default="extend-lockdown")
    parser.add_argument('--transition_mode', action="store",
                        type=int, default='1')
    parser.add_argument('--ci_multiplier', action="store",
                        type=float, default='0.625', help="Multiplier set for Case Isolation which represents the ratio of out-of-house interactions for Covid patients relative to the default interaction rate. Default value comes from Imp Report 9.")
    parser.add_argument('--output_dir', action="store", default=".")
    parser.add_argument('--data_dir', action="store", default="covid_data")
    parser.add_argument('-s','--starting_infections', action="store", default="10")
    parser.add_argument('--start_date', action="store", default="9/21/2020")
    parser.add_argument('-q', '--quicktest', action="store_true", help="set house_ratio to 100 to do quicker (but less accurate) runs for populous regions.")
    parser.add_argument('-g', '--generic_outfile', action="store_true", help="Write main output to out.csv instead of a scenario-specific named file.")
    parser.add_argument('--dbg', action="store_true", help="Write additional outputs to help debugging")
    args = parser.parse_args()
    print(args)

    #Overwrite location types and needs in FACS.
    facs.lids = {'park':0, 'hospital':1, 'supermarket':2, 'office':3, 'school':4, 'leisure':5, 'shopping':6,
        'academic':7,'lecturehall':8, 'library':9, 'sports':10, 'cafe':11, 'bar':12}
    facs.lnames = list(facs.lids.keys())
    facs.needs = facs.Needs("covid_data/needs_campus.csv")

    facs.avg_visit_times = [90,60,60,60,360,360,60,60,360,120,720,60,60,60,60,60,60,15,30] #average time spent per visit


    house_ratio = 1 # default to 1, as these simulations are small.
    if args.quicktest:
      house_ratio = 100
    location = args.location
    ci_multiplier = float(args.ci_multiplier)
    transition_scenario = args.transition_scenario.lower()
    transition_mode = args.transition_mode
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
                    elif row[0].lower() == "transition_scenario":
                        transition_scenario = str(row[1]).lower()
                    elif row[0].lower() == "transition_mode":
                        transition_mode = int(row[1])

    transition_day = -1
    if transition_mode == 1:
        transition_day = 77  
    if transition_mode == 2:
        transition_day = 93 
    if transition_mode == 3:
        transition_day = 108  
    if transition_mode == 4:
        transition_day = 123 
    if transition_mode > 10:
        transition_day = transition_mode

    # check the transition scenario argument
    AcceptableTransitionScenario = ['no-measures', 'extend-lockdown',
                                    'open-all', 'open-schools', 'open-shopping',
                                    'open-leisure', 'work50', 'work75',
                                    'work100', 'dynamic-lockdown', 'periodic-lockdown','uk-forecast']

    if transition_scenario not in AcceptableTransitionScenario:
        print("\nError !\n\tThe input transition scenario, %s , is not VALID" %
              (transition_scenario))
        print("\tThe acceptable inputs are : [%s]" %
              (",".join(AcceptableTransitionScenario)))
        sys.exit()

    # check if output_dir is exists
    if not path.exists(output_dir):
        makedirs(output_dir)

    outfile = "{}/{}-{}-{}.csv".format(output_dir,
                                       location,
                                       transition_scenario,
                                       transition_day)
    if args.generic_outfile:
      outfile = "{}/out.csv".format(output_dir)

    end_time = 180
    if transition_scenario in ["extend-lockdown","dynamic-lockdown","periodic-lockdown","uk-forecast"]:
      end_time = 180

    print("Running basic Covid-19 simulation kernel.")
    print("scenario = %s" % (location))
    print("transition_scenario = %s" % (transition_scenario))
    print("transition_mode = %d" % (transition_mode))
    print("transition_day = %d" % (transition_day))
    print("end_time = %d" % (end_time))
    print("output_dir  = %s" % (output_dir))
    print("outfile  = %s" % (outfile))
    print("data_dir  = %s" % (data_dir))

    e = facs.Ecosystem(end_time, needsfile="covid_data/needs_campus.csv")

    e.ci_multiplier = ci_multiplier
    e.ages = read_age_csv.read_age_csv("{}/age-distr.csv".format(data_dir), location)

    print("age distribution in system:", e.ages, file=sys.stderr)

    e.disease = read_disease_yml.read_disease_yml(
        "{}/disease_covid19.yml".format(data_dir))

    building_file = "{}/{}_buildings.csv".format(data_dir, location)
    #print(building_file)

    households_per_house = 13 #Brunel has large residences, where many households reside. 38*8* ~ 4000

    read_building_csv.read_building_csv(e,
                                        building_file,
                                        "{}/building_types_map_campus.yml".format(data_dir),
                                        house_ratio=house_ratio, workspace=12, office_size=1600, household_size=8, households_per_house=households_per_house, work_participation_rate=0.5)
    # house ratio: number of households per house placed (higher number adds noise, but reduces runtime
    # And then 3 parameters that ONLY affect office placement.
    # workspace: m2 per employee on average. (10 in an office setting, but we use 12 as some people work in more spacious environments)
    # household size: average size of each household, specified separately here.
    # work participation rate: fraction of population in workforce, irrespective of age

    #print("{}/{}_cases.csv".format(data_dir, location))
    # Can only be done after houses are in.
    #read_cases_csv.read_cases_csv(e,
    #                              "{}/{}_cases.csv".format(data_dir, location),
    #                              start_date=args.start_date,
    #                              date_format="%m/%d/%Y")

    starting_num_infections = 500
    if args.starting_infections:
      starting_num_infections = int(args.starting_infections)
    if location == "test":
      starting_num_infections = 10

    for i in range(0,10):
      e.add_infections(int(starting_num_infections/10), i-19)

    #print(e.locations.keys())
    # Enact class groups [type],[number of groups]
    e.make_group("lecturehall",200)
 
    
    print("THIS SIMULATIONS HAS {} AGENTS.".format(e.num_agents))


    e.time = -20
    e.print_header(outfile)
    for i in range(0, 20):
        e.evolve(reduce_stochasticity=False)
        print(e.time)
        if args.dbg:
            e.print_status(outfile)
        else:
            e.print_status(outfile, silent=True)

    track_trace_limit = 0.2 + transition_mode*0.1

    # Initialize code with phase 9 of UK lockdown, as this is in effect in mid Sept.
    measures.uk_lockdown(e, phase=9, track_trace_limit=track_trace_limit)

    for t in range(0, end_time):

        if t == transition_day:
            if transition_scenario == "extend-lockdown":
                pass
            elif transition_scenario == "open-all":
                e.remove_all_measures()

        t_adjusted = t + 204 # Adjusted t for measures to account for a start date in September.

        # Recording of existing measures
        if transition_scenario in ["uk-forecast"]:
          measures.uk_lockdown_forecast(e, t_adjusted, transition_mode)
        elif transition_scenario not in ["no-measures"]:
          measures.uk_lockdown_existing(e, t_adjusted, track_trace_limit=track_trace_limit)

        # Propagate the model by one time step.
        e.evolve()

        print(t)
        e.print_status(outfile)

    print("Simulation complete.", file=sys.stderr)
