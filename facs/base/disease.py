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


    def add_hospitalisation_chances(self, hosp_array: list[list[float]]):
        """Add age-dependent hospitalisation chances."""

        self.hospital = get_interpolated_lists(AGE_CLASSES, hosp_array)

    def add_mortality_chances(self, mort_array: list[list[float]]):
        """Add age-dependent mortality chances."""

        self.mortality = get_interpolated_lists(AGE_CLASSES, mort_array)

    def add_mutations(self, mutations: dict[str, dict]):
        """Add mutations."""

        print("Loading mutations:", mutations, file=sys.stderr)
        self.mutations = mutations
        
    def add_genotypes(self, genotypes: dict[str, dict]):
        """Add genotype with its parameters."""
        
        print("Loading genotypes:", genotypes, file=sys.stderr)
        self.genotypes = genotypes
