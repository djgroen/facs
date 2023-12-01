import os
import sys
import yaml
import warnings

__measure_mask_uptake = 0.0
__measure_mask_uptake_shopping = 0.0
__measure_social_distance = 0.0
__measure_work_from_home = 0.0

def read_measures_yml(e, ymlfile="covid_data/measures.yml"):
    global __measure_mask_uptake, __measure_mask_uptake_shopping, __measure_social_distance, __measure_work_from_home

    if not os.path.exists(ymlfile):
        print("ERROR: measures YML file not found. Exiting.")
        sys.exit()

    with open(ymlfile) as f:
        m = yaml.safe_load(f)

    if m["keyworker_fraction"]:
        e.keyworker_fraction = float(m["keyworker_fraction"])

    date_format = m["date_format"]

    # entry for backwards compatibility
    if date_format == "%d/%m/%Y":
        date_format = "%-d/%-m/%Y"

    date = e.get_date_string(date_format)

    if date in m:
        e.remove_all_measures()

        dm = m[date]

        if "case_isolation" in dm:
            if dm["case_isolation"] == True:
                e.add_case_isolation()
            if dm["case_isolation"] == False:
                e.reset_case_isolation()
        if "household_isolation" in dm:
            if dm["household_isolation"] == True:
                e.add_household_isolation()
            if dm["household_isolation"] == False:
                e.reset_household_isolation()

        if "external_multiplier" in dm:
            e.external_travel_multiplier = float(dm["external_multiplier"])

        if "partial_closure" in dm:
            for pc_key in dm["partial_closure"]:
                e.add_partial_closure(pc_key, dm["partial_closure"][pc_key])

        if "closure" in dm:
            for loc_name in dm["closure"]:
                e.add_closure(
                    loc_name, 0
                )  # add closure starting immediately (indicated by the 0)

        if "work_from_home" in dm:
            __measure_work_from_home = float(dm["work_from_home"])

        e.add_work_from_home(__measure_work_from_home)

        # Social distance variable parsing.
        do_sd = False  # bool to indicate whether social distancing needs to be recalculated.

        if "mask_uptake" in dm:
            __measure_mask_uptake = float(dm["mask_uptake"])
            do_sd = True

        if "mask_uptake_shopping" in dm:
            __measure_mask_uptake_shopping = float(dm["mask_uptake_shopping"])
            do_sd = True

        if "social_distance" in dm:
            __measure_social_distance = float(dm["social_distance"])
            do_sd = True

        e.add_social_distance(
            2.0,
            compliance=__measure_social_distance,
            mask_uptake=__measure_mask_uptake,
            mask_uptake_shopping=__measure_mask_uptake_shopping,
        )

        if "traffic_multiplier" in dm:
            e.traffic_multiplier = float(dm["traffic_multiplier"])

        if "hospital_protection_factor" in dm:
            e.hospital_protection_factor = 1.0 - float(dm["hospital_protection_factor"])

        if "track_trace_efficiency" in dm:
            e.track_trace__multiplier = 1.0 - float(dm["track_trace_efficiency"])

        print(date)
        # print(dm)
