"""Module to store location types and their ids."""

import yaml


def read_building_types(ymlfile: str):
    """Read building types from a YAML file."""

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


_data = read_building_types("covid_data/building_types_map.yml")
building_types_dict = get_building_types(_data)
building_types = _data.keys()
