"""Module for Disease class."""

import sys
from dataclasses import dataclass, field
from .utils import get_interpolated_lists

AGE_CLASSES = 91


@dataclass
class Disease:
    """Class for Disease."""

    # pylint: disable=too-many-instance-attributes

    infection_rate: float
    incubation_period: float
    mild_recovery_period: float
    recovery_period: float
    mortality_period: float
    period_to_hospitalisation: float
    immunity_duration: float

    hospital: list[float] = field(default_factory=list, init=False, repr=False)
    mortality: list[float] = field(default_factory=list, init=False, repr=False)
    mutations: dict[str, dict] = field(default_factory=list, init=False, repr=False)
    genotypes: dict[str, dict] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Ensure that all the parameters are positive floats."""

        positive_attributes = [
            "infection_rate",
            "incubation_period",
            "mild_recovery_period",
            "recovery_period",
            "mortality_period",
            "period_to_hospitalisation",
            "immunity_duration",
        ]

        for attr in positive_attributes:
            if not isinstance(getattr(self, attr), float) and not isinstance(
                getattr(self, attr), int
            ):
                raise TypeError(f"{attr} must be int or float")

            if getattr(self, attr) < 0:
                raise ValueError(f"{attr} must not be negative")

    def array_sanity_check(self, array: list[list[float]], name: str):
        """Sanity check for Hospitalisation and Mortality parameters."""

        for item in array:
            if len(item) != 2:
                raise ValueError(f"{name} chances must be a list of pairs")

        ages = [item[0] for item in array]
        probs = [item[1] for item in array]

        if ages != sorted(ages):
            raise ValueError(f"{name} chances must be sorted by age")

        if min(ages) < 0 or max(ages) > AGE_CLASSES - 1:
            raise ValueError(f"{name} chances must be between 0 and {AGE_CLASSES - 1}")

        if len(ages) != len(set(ages)):
            raise ValueError(f"{name} chances must be unique for each age")

        if min(probs) < 0 or max(probs) > 1:
            raise ValueError(f"{name} chances must be between 0 and 1")

    def dict_sanity_check(self, dictionary: dict[str, dict], name: str):
        """Sanity check for mutations and genotypes parameters."""

        for key in dictionary:
            if not isinstance(dictionary[key], dict):
                raise TypeError(f"{name} must be a dictionary of dictionaries")

            if not isinstance(key, str):
                raise TypeError(f"{name} key must be string")

    def add_hospitalisation_chances(self, hosp_array: list[list[float]]):
        """Add age-dependent hospitalisation chances."""

        self.array_sanity_check(hosp_array, "Hospitalisation")

        self.hospital = get_interpolated_lists(AGE_CLASSES, hosp_array)

    def add_mortality_chances(self, mort_array: list[list[float]]):
        """Add age-dependent mortality chances."""

        self.array_sanity_check(mort_array, "Mortality")

        self.mortality = get_interpolated_lists(AGE_CLASSES, mort_array)

    def add_mutations(self, mutations: dict[str, dict]):
        """Add mutations."""

        self.dict_sanity_check(mutations, "Mutations")

        print("Loading mutations:", mutations, file=sys.stderr)
        self.mutations = mutations

    def add_genotypes(self, genotypes: dict[str, dict]):
        """Add genotype with its parameters."""

        self.dict_sanity_check(genotypes, "Genotypes")

        print("Loading genotypes:", genotypes, file=sys.stderr)
        self.genotypes = genotypes
