import sys
import yaml

def full_lockdown(e):
  e.remove_all_measures()
  e.add_closure("school", 0)
  e.add_closure("leisure", 0)
  e.add_partial_closure("shopping", 0.8)
  # mimicking a 75% reduction in social contacts.
  e.add_social_distance_imp9()
  e.add_work_from_home()
  e.add_case_isolation()
  e.add_household_isolation()


def read_vaccine_yml(e, date, ymlfile="covid_data/vaccinations_example.yml"):
  with open(ymlfile) as f:
    v = yaml.safe_load(f)
  
    vaccine_effect_time = 21
    if "vaccine_effect_time" in v:
      vaccine_effect_time = v["vaccine_effect_time"]
    else:
      print("warning, {} does not contain field vaccine_effect time.".format(ymlfile))

    if date in v:
      dv = v[date]
      if "vaccines_per_day" in dv:
        e.vaccinations_available = int(dv["vaccines_per_day"])
      if "vaccine_age_limit" in dv:
        e.vaccinations_age_limit = int(dv["vaccine_age_limit"])
      if "no_symptoms" in dv:
        e.vac_no_symptoms = float(dv["no_symptoms"])
      if "no_transmission" in dv:
        e.vac_no_transmission = float(dv["no_transmission"])


      #dvb = v[date]["booster"]
      # fields:
      # boosters_per_day: 10 # this number is SUBTRACTED from vaccines_per_day.
      # booster_age_limit: 70
      # no_symptoms: 0.75
      # no_transmission: 0.6
      # TO BE IMPLEMENTED

def read_lockdown_yml(e, date, ymlfile="covid_data/measures_uk.yml"):
  with open(ymlfile) as f:
    m = yaml.safe_load(f)

  keyworker_fraction = 0.2
  if(m["keyworker_fraction"]):
    keyworker_fraction = float(m["keyworker_fraction"])

  if date in m:
    e.remove_all_measures()

    dm = m[date]

    if("case_isolation" in dm):
      if(dm["case_isolation"] == True):
        e.add_case_isolation()
      if(dm["case_isolation"] == False):
        e.reset_case_isolation()
    if("household_isolation" in dm):
      if(dm["household_isolation"] == True):
        e.add_household_isolation()
      if(dm["household_isolation"] == False):
        e.reset_household_isolation()

    if("external_multiplier" in dm):
      e.external_travel_multiplier = float(dm["external_multiplier"])

    if("partial_closure" in dm):
      for pc_key in dm["partial_closure"]:
        e.add_partial_closure(pc_key, dm["partial_closure"][pc_key])

    if("closure" in dm):
      for loc_name in dm["closure"]:
        e.add_closure(loc_name, 0) # add closure starting immediately (indicated by the 0)

    if("work_from_home" in dm):
      e.add_work_from_home(float(dm["work_from_home"]))

    mask_uptake = 0.0
    if("mask_uptake" in dm):
      mask_uptake = float(dm["mask_uptake"])

    mask_uptake_shopping = 0.0
    if("mask_uptake_shopping" in dm):
      mask_uptake_shopping = float(dm["mask_uptake_shopping"])

    if("social_distance" in dm):
      e.add_social_distance(compliance = float(dm["social_distance"]), mask_uptake=mask_uptake, mask_uptake_shopping=mask_uptake_shopping)

    if("traffic_multiplier" in dm):
      e.traffic_multiplier = float(dm["traffic_multiplier"])

    if("track_trace_efficiency" in dm):
      e.track_trace__multiplier = 1.0 - float(dm["track_trace_efficiency"])

    print(date)
    print(dm)


def update_hospital_protection_factor_uk(e, t):
  e.hospital_protection_factor = 0.4
  if t == 20:
    e.hospital_protection_factor = 0.35
  if t == 30: # start of testing ramp up in early april.
    e.hospital_protection_factor = 0.3
  if t == 40:
    e.hospital_protection_factor = 0.26
  if t == 50:
    e.hospital_protection_factor = 0.23
  if t == 60: # testing ramped up considerably by the end of April.
    e.hospital_protection_factor = 0.16
  if t == 80:
    e.hospital_protection_factor = 0.12
  if t == 100:
    e.hospital_protection_factor = 0.10


def uk_lockdown_existing(e, t, track_trace_limit=0.5):
  update_hospital_protection_factor_uk(e,t)

  e.vac_duration = 273
  e.immunity_duration = 273

  read_lockdown_yml(e, e.get_date_string())

  
  # traffic multiplier = relative reduction in travel minutes^2 / relative reduction service minutes
  # Traffic: Mar 10: 90% (estimate), Mar 16: 60%, Mar 20: 20%, Mar 28: 10%
  # Service: Mar 20: 80%, Mar 28: 50%
  if t > 10 and t <= 15:
    e.traffic_multiplier = ((0.9 - (0.06*(t-10)))**2) / 1.0
  if t > 15 and t <= 20:
    e.traffic_multiplier = ((0.6 - (0.08*(t-15)))**2) / 0.8
  if t > 20 and t <= 28:
    e.traffic_multiplier = ((0.2 - (0.0125*(t-20)))**2) / 0.5


def calculate_mutating_infection_rate(fraction, source=0.07, dest=0.1):
  # Original infection rate is 0.07 (COVID-19 disease.yml)
  # destination infection rate is "up to 70% higher", so we set it to 0.07*1.5=0.105.

  if fraction > 1.0:
    print("Error: fraction > 1.0", file=sys.stderr)
    sys.exit()

  return 2.0*(1.0-fraction)*source + (fraction*dest) #always return double of the base infection rate value, as FACS assumes 100% infectious persons (not 50%), see disease.py.


def uk_lockdown_forecast(e, t, mode = 0):

  # add in Alpha mutation
  # Prevalence increases linearly from Oct 22 (1%) to Jan 30th (100%)
  if t > 235 and t < 336:
    a = e.disease.infection_rate
    fraction = (t - 235) * 0.01
    e.disease.infection_rate = calculate_mutating_infection_rate(fraction, 0.07, 0.11) # https://cmmid.github.io/topics/covid19/uk-novel-variant.html
    print("infection rate adjusted from ",a," to ", e.disease.infection_rate, file=sys.stderr)

  # add in Delta mutation
  # Prevalence increases linearly from Apr 21 (1%) to June 10th (100%)
  if t > 416 and t < 467:
    fraction = (t - 416) * 0.02
    e.disease.infection_rate = calculate_mutating_infection_rate(fraction, 0.11, 0.165) # https://www.ecdc.europa.eu/en/publications-data/threat-assessment-emergence-and-impact-sars-cov-2-delta-variant
    # our estimate is 50% here, as Delta gains full dominance in this period.
    # https://www.gov.uk/government/news/confirmed-cases-of-covid-19-variants-identified-in-uk#:~:text=The%20Delta%20variant%20currently%20accounts,of%20cases%20across%20the%20UK.&text=In%20total%2C%203%2C692%20people%20have,the%20Delta%20and%20Beta%20variants.l
    print("infection rate adjusted to ", e.disease.infection_rate, file=sys.stderr)

  read_vaccine_yml(e, e.get_date_string())

  uk_lockdown_existing(e, t)


def work50(e):
  e.remove_all_measures()
  e.add_closure("school", 0)
  e.add_closure("leisure", 0)
  e.add_partial_closure("shopping", 0.4)
  # mimicking a 75% reduction in social contacts.
  e.add_social_distance_imp9()
  # light work from home instruction, with 50% compliance
  e.add_work_from_home(0.5)
  e.add_case_isolation()
  e.add_household_isolation()


def work75(e):
  e.remove_all_measures()
  e.add_partial_closure("leisure", 0.5)
  # mimicking a 75% reduction in social contacts.
  e.add_social_distance_imp9()
  # light work from home instruction, with 25% compliance
  e.add_work_from_home(0.25)
  e.add_case_isolation()
  e.add_household_isolation()

def work100(e):
  e.remove_all_measures()
  # mimicking a 75% reduction in social contacts.
  e.add_social_distance_imp9()
  e.add_case_isolation()
  e.add_household_isolation()

