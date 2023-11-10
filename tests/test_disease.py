"""Tests for the Disease class."""

import pytest
from facs.base.disease import Disease

AGE_CLASSES = 91

# pylint: disable=redefined-outer-name


@pytest.fixture
def disease():
    return Disease(
        infection_rate=0.05,
        incubation_period=5.0,
        mild_recovery_period=10.0,
        recovery_period=15.0,
        mortality_period=20.0,
        period_to_hospitalisation=25.0,
        immunity_duration=30.0,
    )


def test_disease_initialization(disease: Disease):
    """Test Disease initialization."""

    assert (
        repr(disease) == "Disease(infection_rate=0.05, "
        "incubation_period=5.0, mild_recovery_period=10.0, "
        "recovery_period=15.0, mortality_period=20.0, "
        "period_to_hospitalisation=25.0, immunity_duration=30.0)"
    )


def test_add_hospitalisation_chances(disease: Disease):
    """Test adding hospitalisation chances."""

    hosp_array = [[0, 0.1], [90, 0.2]]
    disease.add_hospitalisation_chances(hosp_array)
    assert len(disease.hospital) == AGE_CLASSES
    assert disease.hospital[0] == 0.1
    assert disease.hospital[AGE_CLASSES - 1] == 0.2
    assert min(disease.hospital) == 0.1
    assert max(disease.hospital) == 0.2


def test_add_mortality_chances(disease: Disease):
    """Test adding mortality chances."""

    mort_array = [[0, 0.05], [90, 0.1]]
    disease.add_mortality_chances(mort_array)
    assert len(disease.mortality) == AGE_CLASSES
    assert disease.mortality[0] == 0.05
    assert disease.mortality[AGE_CLASSES - 1] == 0.1
    assert min(disease.mortality) == 0.05
    assert max(disease.mortality) == 0.1


def test_add_mutations(disease: Disease):
    """Test adding mutations."""

    mutations = {"mutation1": {"effect": 1.2}}
    disease.add_mutations(mutations)
    assert disease.mutations == mutations


def test_add_genotypes(disease):
    """Test adding genotypes."""

    genotypes = {"genotype1": {"effect": 1.1}}
    disease.add_genotypes(genotypes)
    assert disease.genotypes == genotypes
