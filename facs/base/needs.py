"""Module for generating needs for the population."""

import os
import pandas as pd


class Needs:
    """Generates needs for the population."""

    def __init__(self, filename: str, building_types: list[str]):
        """Add needs from a CSV file."""

        self.needs = pd.read_csv(filename, header=0, index_col=0)

        if set(self.needs.columns) != set(building_types):
            print(self.needs.columns)
            raise ValueError("Needs file does not contain all location types.")

        # assuming 25% of school time is outside of the building (PE or breaks)
        self.needs["school"] = self.needs["school"] * 0.75
        self.needs["school"] = self.needs["school"].astype(int)
        self.needs = self.needs.reindex(building_types, axis=1)

        print(f"Needs created from {filename}.")

    def exception_handler(self, filename: str):
        """Check if the filename is valid."""

        if not os.path.exists(filename):
            raise FileNotFoundError("Needs file not found.")

        if not os.path.isfile(filename):
            raise ValueError("Needs file is not a file.")

        if filename.split(".")[-1] != "csv":
            raise ValueError("Needs file must be a CSV.")

    def get_needs(self, person):
        """Get the needs of a person."""

        # Type hint for person to be added

        if not person.hospitalised:
            need = dict(self.needs.iloc[person.age])
            if person.work_from_home:
                need["office"] = 0
            if person.school_from_home:
                need["school"] = 0
            return list(need.values())

        return [0, 5040, 0, 0, 0, 0, 0]

    def scale_needs(self, location_type, factor):
        """Scale the needs of a location type by a factor."""

        self.needs[location_type] = self.needs[location_type] * factor
