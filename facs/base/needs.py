"""Module for generating needs for the population."""

from __future__ import annotations
import os
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from facs.base.person import Person


class Needs:
    """Generates needs for the population and tracks statistics."""

    def __init__(self, filename: str, building_types: list[str]):
        """Initialize Needs from a CSV file and compute basic statistics."""

        self.exception_handler(filename)

        # Load needs from CSV
        self.needs = pd.read_csv(filename, header=0, index_col=0)

        if set(self.needs.columns) != set(building_types):
            print(f"Error: CSV contains columns {self.needs.columns}, expected {building_types}")
            raise ValueError("Needs file does not contain all location types.")

        # Adjust school needs (assuming 25% of time is outside the building)
        self.needs["school"] = (self.needs["school"] * 0.75).astype(int)

        # Ensure the column order matches the building types list
        self.needs = self.needs.reindex(building_types, axis=1)

    def exception_handler(self, filename: str):
        """Check if the filename is valid before loading."""

        if not os.path.exists(filename):
            raise FileNotFoundError(f"Needs file '{filename}' not found.")

        if not os.path.isfile(filename):
            raise ValueError(f"'{filename}' is not a file.")

        if not filename.endswith(".csv"):
            raise ValueError(f"Needs file '{filename}' must be a CSV.")

    def get_needs(self, person: Person):
        """Retrieve the needs of a given person, adjusting for WFH and hospitalization."""

        if not person.hospitalised:
            need = dict(self.needs.iloc[person.age])  # Retrieve needs for person's age

            # Adjust based on individual conditions
            if person.work_from_home:
                need["office"] = 0
            if person.school_from_home:
                need["school"] = 0

            return list(need.values())

        # If hospitalized, override with hospital needs
        return [0, 5040, 0, 0, 0, 0, 0]

    def scale_needs(self, location_type: str, factor: float):
        """Scale the needs of a location type by a factor."""

        if location_type not in self.needs.columns:
            raise ValueError(f"Location type '{location_type}' not found in needs.")

        if factor < 0:
            raise ValueError("Scale factor must be positive.")

        self.needs[location_type] *= factor
        print(f"Scaled needs for '{location_type}' by a factor of {factor}.")

    def compute_needs_statistics(self):
        """Compute and print statistics about total time spent in each location."""

        total_time_spent = self.needs.sum().sort_values(ascending=False)
        ranked_locations = {location: time for location, time in total_time_spent.items()}
        
        print("Ranked Location needs by Total Time Spent: ")
        print(ranked_locations)

    def get_most_visited_location(self):
        """Return the most visited location type based on total needs."""
        return self.needs.sum().idxmax()
