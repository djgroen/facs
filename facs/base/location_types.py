"""Module to store location types and their ids."""

import os
import sys
import yaml


def read_building_types(data_dir="covid_data", ymlfile=None):
    """Read building types from a YAML file."""
    
    # Set the default file path if none is provided
    if ymlfile is None:
        ymlfile = f"{data_dir}/building_types_map.yml"

    # Check if the file exists
    if not os.path.exists(ymlfile):
        print(f"ERROR: Building types YML file not found at {ymlfile}. Exiting.")
        sys.exit()

    with open(ymlfile, encoding="utf-8") as file:
        buildings_data = yaml.safe_load(file)

    types = {}

    for building_type, params in buildings_data.items():
        index = params.get("index", None)
        labels = params.get("labels", [])
        default_sqm = params.get("default_sqm", 0)

        types[building_type] = {
            "index": index,
            "labels": labels,
            "default_sqm": default_sqm,
        }

    return types


def get_building_types(types):
    """Get a dictionary of building types and their ids."""

    buildings = {}

    for building_type, data in types.items():
        index = data["index"]
        buildings[building_type] = index

    return buildings

# Default data directory (will be updated dynamically)
data_dir = "covid_data"

# Dynamically load building types
_data = read_building_types(data_dir)
building_types_dict = get_building_types(_data)
building_types = _data.keys()

# Load full building type data dynamically
with open(f"{data_dir}/building_types_map.yml", encoding="utf-8") as f:
    building_types_data = yaml.safe_load(f)
