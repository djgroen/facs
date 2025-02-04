import sys
import warnings
from datetime import datetime, timedelta
import yaml

__mutation_daily_change = 0.0
__mutation_days_remaining = -1

def read_vaccinations_yml(e, base_date, data_dir, ymlfile, diseasefile):
    global __mutation_daily_change, __mutation_days_remaining
    with open(ymlfile, "r", encoding="utf-8") as f:
        v = yaml.safe_load(f)

    with open(diseasefile, "r", encoding="utf-8") as g:
        w = yaml.safe_load(g)

        if "vaccine_effect_time" in v:
            e.vaccine_effect_time = v["vaccine_effect_time"]
        else:
            e.vaccine_effect_time = 14
            warnings.warn(
                f"vaccine_effect_time not found in {ymlfile}, using default value of 14 days."
            )

        if "immunity_duration" not in w:
            raise KeyError(
                f"immunity_duration not found in {diseasefile}, please add it."
            )

        e.vac_duration = w["immunity_duration"]

        if e.vac_duration < 0:
            raise ValueError("immunity_duration cannot be negative")

        tmpdate = datetime.strptime(base_date, "%d/%m/%Y")
        tmpdate = tmpdate - timedelta(days=e.vaccine_effect_time)
        date = tmpdate.strftime("%-d/%-m/%Y")

        # print(date,v)

        if date in v:
            dv = v[date]
            if "vaccines_per_day" in dv:
                e.vaccinations_available = int(dv["vaccines_per_day"]) / e.mpi.size
            if "vaccine_age_limit" in dv:
                e.vaccinations_age_limit = int(dv["vaccine_age_limit"])
            if "no_symptoms" in dv:
                e.vac_no_symptoms = float(dv["no_symptoms"])
            if "no_transmission" in dv:
                e.vac_no_transmission = float(dv["no_transmission"])

            # dvb = v[date]["booster"]
            # fields:
            # boosters_per_day: 10 # this number is SUBTRACTED from vaccines_per_day.
            # booster_age_limit: 70
            # no_symptoms: 0.75
            # no_transmission: 0.6
            # TO BE IMPLEMENTED

    verbose = False
    try:
        with open(f"{data_dir}/mutations.yml") as f:
            v = yaml.safe_load(f)

        with open(diseasefile) as g:
            w = yaml.safe_load(g)

            if base_date in v:
                dv = v[base_date]
                new_inf_rate = w["mutations"][dv["type"]]["infection_rate"]
                e.disease.mutations[dv["type"]]["infection_rate"] = new_inf_rate
                __mutation_daily_change = (
                    new_inf_rate - e.disease.infection_rate
                ) / int(dv["transition_period"])
                __mutation_days_remaining = int(dv["transition_period"])

                # print("Mutation started to {}, inf. rate {}, transition period {}, daily change {}".format(dv["type"], new_inf_rate, dv["transition_period"], __mutation_daily_change))
    except FileNotFoundError:
        if verbose:
            print(
                f"WARNING: {data_dir}/mutations.yml OR {diseasefile} not found"
            )

    if __mutation_days_remaining > 0:
        e.disease.infection_rate += __mutation_daily_change
        __mutation_days_remaining -= 1

