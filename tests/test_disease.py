"""Tests for the Disease class."""

import pytest
from facs.base.disease import Disease

AGE_CLASSES = 91

# pylint: disable=redefined-outer-name


@pytest.fixture
def disease():
    """Return a Disease instance."""

    return Disease(
        name="COVID-19",
        infection_rate=0.05,
        incubation_period=5.0,
        mild_recovery_period=10.0,
        recovery_period=15.0,
        mortality_period=20.0,
        period_to_hospitalisation=25.0,
        immunity_duration=30.0,
        immunity_fraction=0.5,
    )


def test_disease_initialization(disease: Disease):
    """Test Disease initialization."""

    assert (
        repr(disease) == "Disease(name='COVID-19', infection_rate=0.05, "
        "incubation_period=5.0, mild_recovery_period=10.0, "
        "recovery_period=15.0, mortality_period=20.0, "
        "period_to_hospitalisation=25.0, immunity_duration=30.0, immunity_fraction=0.5)"
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


def test_add_genotypes(disease: Disease):
    """Test adding genotypes."""

    genotypes = {"genotype1": {"effect": 1.1}}
    disease.add_genotypes(genotypes)
    assert disease.genotypes == genotypes


def test_disease_initialisation_warn_zero_parameters():
    """Test Disease initialization with zero parameters."""

    with pytest.warns(RuntimeWarning):
        Disease(
            name="COVID-19",
            infection_rate=0.0,
            incubation_period=5.0,
            mild_recovery_period=10.0,
            recovery_period=15.0,
            mortality_period=20.0,
            period_to_hospitalisation=25.0,
            immunity_duration=30.0,
            immunity_fraction=0.5,
        )


def test_disease_initialisation_fail_negative_parameters():
    """Test Disease initialization with negative parameters."""

    with pytest.raises(ValueError):
        Disease(
            name="COVID-19",
            infection_rate=-0.05,
            incubation_period=5.0,
            mild_recovery_period=10.0,
            recovery_period=15.0,
            mortality_period=20.0,
            period_to_hospitalisation=25.0,
            immunity_duration=30.0,
            immunity_fraction=0.5,
        )


def test_disease_initialisation_fail_string_parameters():
    """Test Disease initialization with string parameters."""

    with pytest.raises(TypeError):
        Disease(
            name="COVID-19",
            infection_rate="0.05",
            incubation_period=5.0,
            mild_recovery_period=10.0,
            recovery_period=15.0,
            mortality_period=20.0,
            period_to_hospitalisation=25.0,
            immunity_duration=30.0,
            immunity_fraction=0.5,
        )


def test_disease_initialisation_invalid_immunity_fraction():
    """Test Disease initialization with string parameters."""

    with pytest.raises(TypeError):
        Disease(
            name="COVID-19",
            infection_rate="0.05",
            incubation_period=5.0,
            mild_recovery_period=10.0,
            recovery_period=15.0,
            mortality_period=20.0,
            period_to_hospitalisation=25.0,
            immunity_duration=30.0,
            immunity_fraction=1.5,
        )


def test_disease_initialisation_fail_list_parameters():
    """Test Disease initialization with list parameters."""

    with pytest.raises(TypeError):
        Disease(
            name="COVID-19",
            infection_rate=[0.05],
            incubation_period=5.0,
            mild_recovery_period=10.0,
            recovery_period=15.0,
            mortality_period=20.0,
            period_to_hospitalisation=25.0,
            immunity_duration=30.0,
            immunity_fraction=0.5,
        )


def test_disease_initialisation_fail_negative_hospitalisation(disease: Disease):
    """Test Disease initialization with negative hospitalisation chances."""

    hosp_array = [[0, -0.1], [90, 0.2]]
    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array)


def test_disease_initialisation_fail_hospitalisation_not_sorted(disease: Disease):
    """Test Disease initialization with unsorted hospitalisation chances."""

    hosp_array = [[90, 0.2], [0, 0.1]]
    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array)


def test_disease_initialisation_fail_hospitalisation_not_unique(disease: Disease):
    """Test Disease initialization with non-unique ages."""

    hosp_array = [[0, 0.1], [0, 0.2]]
    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array)


def test_disease_initialisation_fail_hospitalisation_age_out_of_range(disease: Disease):
    """Test Disease initialization with hospitalisation age out of range."""

    hosp_array1 = [[0, 0.1], [91, 0.2]]
    hosp_array2 = [[-1, 0.1], [90, 0.2]]

    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array1)

    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array2)


def test_disease_initialisation_fail_hospitalisation_prob_out_of_range(
    disease: Disease,
):
    """Test Disease initialization with hospitalisation probability out of range."""

    hosp_array1 = [[0, -0.1], [90, 0.2]]
    hosp_array2 = [[0, 0.1], [90, 1.2]]

    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array1)

    with pytest.raises(ValueError):
        disease.add_hospitalisation_chances(hosp_array2)


def test_disease_initialisation_fail_mortality_uneven_array(disease: Disease):
    """Test Disease initialization with uneven mortality array."""

    mort_array = [[0, 0.1], [90, 0.2, 0.1]]
    with pytest.raises(ValueError):
        disease.add_mortality_chances(mort_array)


def test_disease_initialisation_fail_mutation_not_dict(disease: Disease):
    """Test Disease initialization with non-dict mutation."""

    mutations = {"mutation1": 1.2}
    with pytest.raises(TypeError):
        disease.add_mutations(mutations)


def test_disease_initialisation_fail_mutation_not_str(disease: Disease):
    """Test Disease initialization with non-dict mutation."""

    mutations = {1: {"infection_rate": 1.2}}
    with pytest.raises(TypeError):
        disease.add_mutations(mutations)
