import sys

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

def uk_lockdown(e, phase=1, transition_fraction=1.0, keyworker_fraction=0.18):
  """
  Code which reflects EXISTING UK lockdown measures.
  """
  e.remove_all_measures()
  transition_fraction = max(0.0, min(1.0, transition_fraction))
  keyworker_fraction = max(0.0, min(1.0, keyworker_fraction))

  if phase == 1: # Enacted March 16th
    e.add_partial_closure("leisure", 0.5)
    e.add_social_distance(compliance=transition_fraction*0.75, mask_uptake=transition_fraction*0.05)
    # light work from home instruction, with ascending compliance to 60%.
    e.add_work_from_home(0.65*transition_fraction)
  if phase == 2: # Enacted March 23rd
    e.add_partial_closure("school", 1.0 - keyworker_fraction, exclude_people=True)
    e.add_closure("leisure", 0)
    e.add_partial_closure("shopping", 0.6 + (transition_fraction * 0.2))
    e.add_social_distance(compliance=0.65 + (transition_fraction * 0.1), mask_uptake=0.05)
    e.add_work_from_home(0.9 - keyworker_fraction + (transition_fraction * 0.1)) # www.ifs.org.uk/publications/14763 (18% are key worker in London)
  if phase == 3: # Enacted April 22nd
    e.add_partial_closure("school", 1.0 - keyworker_fraction, exclude_people=True)
    e.add_closure("leisure", 0)
    e.add_partial_closure("shopping", 0.8)
    e.add_social_distance(compliance=0.8, mask_uptake=0.15)
    e.add_work_from_home(1.0 - keyworker_fraction) # www.ifs.org.uk/publications/14763 (18% are key worker in London)
  if phase == 4: # Enacted May 13th
    e.add_partial_closure("school", 1.0 - keyworker_fraction, exclude_people=True)
    e.add_closure("leisure", 0)
    e.add_partial_closure("shopping", 0.6)
    e.add_social_distance(compliance=0.7, mask_uptake=0.2)
    e.add_work_from_home(0.7)
    e.ci_multiplier *= 0.7 # Assumption: additional directives for those with anosmia to stay home improves compliance by 30%.
  if phase == 5: # Enacted June 1st
    e.add_partial_closure("school", (1.0 - keyworker_fraction) / 2.0, exclude_people=True)
    e.add_closure("leisure", 0)
    e.add_partial_closure("shopping", 0.6)
    e.add_social_distance(compliance=0.7, mask_uptake=0.2)
    e.add_work_from_home(0.7)
  if phase == 6: # Enacted June 15th
    e.add_partial_closure("school", (1.0 - keyworker_fraction) / 2.0, exclude_people=True)
    e.add_closure("leisure", 0)
    e.add_partial_closure("shopping", 0.2)
    e.add_social_distance(compliance=0.7, mask_uptake=0.2)
    e.add_work_from_home(0.65)
    e.enforce_face_masks_on_transport()
  if phase == 7: # Enacted July 4th
    e.add_partial_closure("school", (1.0 - keyworker_fraction) / 2.0, exclude_people=True)
    e.add_partial_closure("leisure", 0.8)
    e.add_partial_closure("shopping", 0.1)
    e.add_social_distance(compliance=0.7, mask_uptake=0.2)
    e.add_work_from_home(0.65)
  if phase == 7: # Enacted July 15th
    e.add_partial_closure("school", (1.0 - keyworker_fraction) / 2.0, exclude_people=True)
    e.add_partial_closure("leisure", 0.3)
    e.add_social_distance(compliance=0.7, mask_uptake=0.2)
    e.add_work_from_home(0.65)
    e.enforce_face_masks_in_shops()


  # mimicking a 75% reduction in social contacts.
  #e.add_social_distance_imp9()

  e.add_case_isolation()
  e.add_household_isolation()


def update_hospital_protection_factor_uk(e, t):
  if t == 10:
    e.hospital_protection_factor = 0.4
  if t == 20:
    e.hospital_protection_factor = 0.37
  if t == 30: # start of testing ramp up in early april.
    e.hospital_protection_factor = 0.34
  if t == 40:
    e.hospital_protection_factor = 0.29
  if t == 50:
    e.hospital_protection_factor = 0.23
  if t == 60: # testing ramped up considerably by the end of April.
    e.hospital_protection_factor = 0.16
  if t == 80:
    e.hospital_protection_factor = 0.12
  if t == 100:
    e.hospital_protection_factor = 0.10
  if t == 120:
    e.hospital_protection_factor = 0.08


def uk_lockdown_scenarios(e, t, step, vaccine=100, track_trace_multiplier = 0.5):
  e.remove_all_measures()

  if step == 2: # June 1st, planned school opening
    e.add_partial_closure("school", 0.5) #school times halved
    e.add_partial_closure("school", 0.75, exclude_people=True) #25% of students go.
    e.add_closure("leisure", 0)
    e.add_partial_closure("shopping", 0.6)
    e.add_social_distance(compliance=0.7, mask_uptake=0.2)
    e.add_work_from_home(0.7)

  if step == 3: # 70% of students go to  school, first leisure locs open
    e.add_partial_closure("school", 0.5)
    e.add_partial_closure("school", 0.3, exclude_people=True) #70% of students go.
    e.add_partial_closure("leisure", 0.75)
    e.add_partial_closure("shopping", 0.4)
    e.add_social_distance(compliance=0.7, mask_uptake=0.3)
    e.add_work_from_home(0.4)

  if step == 4: # all schools open
    e.add_partial_closure("school", 0.5)
    e.add_partial_closure("leisure", 0.5)
    e.add_partial_closure("shopping", 0.2)
    e.add_social_distance(compliance=0.7, mask_uptake=0.3)
    e.add_work_from_home(0.3)

  if step == 5: # track and trace in place.
    e.add_partial_closure("school", 0.5)
    e.add_partial_closure("leisure", 0.5)
    e.add_social_distance(compliance=0.7, mask_uptake=0.3)
    e.add_work_from_home(0.25)
    # Assumption: track and trace will render case isolation twice as effective.
    e.ci_multiplier *= track_trace_multiplier

  if step == 6: # vaccine in place. Schools fully open.
    e.add_social_distance(compliance=0.7, mask_uptake=0.3)
    e.add_work_from_home(0.25)
    e.vaccinations_available += vaccine

  if step == 7: # 50% vaccination coverage.
    e.add_social_distance(compliance=0.7, mask_uptake=0.3)
    e.add_work_from_home(0.25)
    e.vaccinations_available += vaccine*10

  e.add_case_isolation()
  e.add_household_isolation()
   
def uk_lockdown_existing(e, t):
  update_hospital_protection_factor_uk(e,t)

  # traffic multiplier = relative reduction in travel minutes^2 / relative reduction service minutes
  # Traffic: Mar 10: 90% (estimate), Mar 16: 60%, Mar 20: 20%, Mar 28: 10%
  # Service: Mar 20: 80%, Mar 28: 50%
  if t > 10 and t <= 15:
    e.traffic_multiplier = ((0.9 - (0.06*(t-10)))**2) / 1.0
  if t > 15 and t <= 20:
    e.traffic_multiplier = ((0.6 - (0.08*(t-15)))**2) / 0.8
  if t > 20 and t <= 28:
    e.traffic_multiplier = ((0.2 - (0.0125*(t-20)))**2) / 0.5

  # Recording of existing measures
  if t > 10 and t <= 20:  # 16th of March (range 11-21)
    uk_lockdown(e, phase=1, transition_fraction=((t-10)*1.0)/100.0)
  if t > 22 and t <= 32:  # 23rd of March, t=22
    uk_lockdown(e, phase=2, transition_fraction=((t-22)*1.0)/100.0)
  if t == 52:  # 22nd of April
    uk_lockdown(e, phase=3)
  if t == 73: # 13th of May
    uk_lockdown(e, phase=4)

def uk_lockdown_forecast(e, t, mode = 0):

  # 0 = default
  # 1 = 1 month delay
  # 2 = september 3 month delay
  # 3 = increased track and trace
  # 4 = reduced track and trace
  # 5 = 50% vaccine
  # 6 = 25% vaccine
  # 7 = no vaccine
  # 8 = temporary immunity


  delay = 0
  if mode == 1:
    delay += 30

  delay3 = 0
  if mode == 2:
    delay3 = 92

  track_trace_multiplier = 0.5
  if mode == 3:
    track_trace_multiplier = 0.25
  if mode == 4:
    track_trace_multiplier = 0.75

  vaccine = 100
  if mode == 5:
    vaccine = 50
  if mode == 6:
    vaccine = 25
  if mode == 7:
    vaccine = 0


  if t<74:
    uk_lockdown_existing(e, t)
  else:
    if t == 92+delay: # June 1st
      uk_lockdown_scenarios(e, t, 2)
    if t == 122+delay+delay3: # July 1st
      uk_lockdown_scenarios(e, t, 3)
    if t == 184+delay+delay3: # September 1st
      uk_lockdown_scenarios(e, t, 4)
    if t == 306+delay+delay3: # January 1st 2021
      uk_lockdown_scenarios(e, t, 5, track_trace_multiplier=track_trace_multiplier)
    if t == 365+delay+delay3: # March 1st 2021
      uk_lockdown_scenarios(e, t, 6, vaccine=vaccine)
    if t == 487+delay+delay3: # July 1st 2021
      uk_lockdown_scenarios(e, t, 7, vaccine=vaccine)

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

_dyn_lock_full = True # we assume this mechanism starts in lockdown mode.
def enact_dynamic_lockdown(e, light_lockdown_func, kpi_value, threshold):
  """
  Dynamic lockdown based on threshold KPI assessment.
  """
  global _dyn_lock_full
  if kpi_value > threshold:
    if not _dyn_lock_full:
      print("DYNAMIC: Full lockdown", file=sys.stderr)
      full_lockdown(e)
      _dyn_lock_full = True
  else:
    if _dyn_lock_full:
      print("DYNAMIC: Light lockdown", file=sys.stderr)
      light_lockdown_func(e)
      _dyn_lock_full = False


def enact_periodic_lockdown(e, light_lockdown_func):
  """
  Dynamic lockdown based on static time intervals.
  """
  global _dyn_lock_full
  if not _dyn_lock_full:
    print("PERIODIC: Full lockdown", file=sys.stderr)
    full_lockdown(e)
    _dyn_lock_full = True
  else:
    print("PERIODIC: Light lockdown", file=sys.stderr)
    light_lockdown_func(e)
    _dyn_lock_full = False
