import os
import sys
import warnings
from datetime import datetime, timedelta

import yaml

from facs.readers.read_measures_yml import read_measures_yml
from facs.readers.read_vaccinations_yml import read_vaccinations_yml

import os
import sys
import warnings
from datetime import datetime, timedelta
import yaml

class Measures:
    def __init__(self):
        pass
        # Initialize the Measures class attributes here

    def calculate_mutating_infection_rate(self, fraction, source=0.07, dest=0.1):
        # Original infection rate is 0.07 (COVID-19 disease.yml)
        # destination infection rate is "up to 70% higher", so we set it to 0.07*1.6=0.112.

        if fraction > 1.0:
            print("Error: fraction > 1.0", file=sys.stderr)
            sys.exit()

        return (1.0 - fraction) * source + (fraction * dest)

    def enact_measures_and_evolutions(self, e, t, data_dir, measures_yml, vaccinations_yml, disease_yml):
        # add in Alpha mutation
        # Prevalence increases linearly from Oct 22 (1%) to Jan 20th (100%)
        # if t > 235 and t < 316:
        #  a = e.disease.infection_rate
        #  fraction = (t - 235) * 0.0125
        #  e.disease.infection_rate = calculate_mutating_infection_rate(fraction, 0.07, 0.112) # https://cmmid.github.io/topics/covid19/uk-novel-variant.html
        #  print("infection rate adjusted from ",a," to ", e.disease.infection_rate, file=sys.stderr)

        # add in Delta mutation
        # Prevalence increases linearly from Apr 21 (1%) to June 10th (100%)
        # if t > 416 and t < 467:
        #  fraction = (t - 416) * 0.02
        #  e.disease.infection_rate = calculate_mutating_infection_rate(fraction, 0.112, 0.165) # https://www.ecdc.europa.eu/en/publications-data/threat-assessment-emergence-and-impact-sars-cov-2-delta-variant

        #  # our estimate is 50% here, as Delta gains full dominance in this period.
        #  # https://www.gov.uk/government/news/confirmed-cases-of-covid-19-variants-identified-in-uk#:~:text=The%20Delta%20variant%20currently%20accounts,of%20cases%20across%20the%20UK.&text=In%20total%2C%203%2C692%20people%20have,the%20Delta%20and%20Beta%20variants.l
        #  print("infection rate adjusted to ", e.disease.infection_rate, file=sys.stderr)
        read_vaccinations_yml(
            e,
            e.get_date_string(),
            data_dir,
            f"{data_dir}/{vaccinations_yml}.yml",
            f"{data_dir}/{disease_yml}.yml",
        )
        read_measures_yml(e, data_dir, f"{data_dir}/{measures_yml}.yml")
        
