import csv
import sys
import pprint
import yaml
from facs.base import disease

pp = pprint.PrettyPrinter()

def read_disease_yml(ymlfile="covid_data/disease-covid19.yml"):

  with open(ymlfile) as f:
    dp = yaml.safe_load(f)

  print(dp)
  d = disease.Disease(dp["infection_rate"], dp["incubation_period"], dp["mild_recovery_period"], dp["recovery_period"], dp["mortality_period"], dp["period_to_hospitalisation"], dp["immunity_duration"])
  d.addHospitalisationChances(dp["hospitalised"])
  d.addMortalityChances(dp["mortality"])
  d.addMutations(dp["mutations"])
  d.print()
  return d


