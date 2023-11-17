"""Test the Household class in the base module."""

import random

from unittest import mock
from unittest.mock import Mock

import pytest

from facs.base.household import Household
from facs.base.house import House

# pylint: disable=redefined-outer-name


@pytest.fixture
def sample_house():
    """Return a sample House object."""
    return House(0, 0)


@pytest.fixture
def sample_ages():
    """Return a sample list of ages."""
    probs = list(random.random() for _ in range(91))
    probs = [p / sum(probs) for p in probs]
    return probs


# Test functions


def test_household_initialization(sample_house, sample_ages):
    """Test the initialization of Household class."""

    household = Household(sample_house, sample_ages, size=3)
    assert household.house == sample_house
    assert household.ages == sample_ages
    assert len(household.agents) == household.size


def test_get_infectious_count_type(sample_house, sample_ages):
    """Test get_infectious_count method in Household class."""

    household = Household(sample_house, sample_ages)
    assert isinstance(household.get_infectious_count(), int)


def test_is_infected_type(sample_house, sample_ages):
    """Test is_infected method in Household class."""

    household = Household(sample_house, sample_ages)
    # Manipulate the agents' statuses here to test different scenarios
    assert isinstance(household.is_infected(), bool)


def test_get_infected_value(sample_house, sample_ages):
    """Test evolve method in Household class."""

    household = Household(sample_house, sample_ages, size=3)

    assert household.get_infectious_count() == 0

    household.agents[random.randint(0, 2)].status = "infectious"
    infectious = household.get_infectious_count()

    assert infectious == 1


@mock.patch("facs.base.household.probability", return_value=1.0)
def test_evolve(mock_probability, sample_house, sample_ages):
    """Test evolve method in Household class."""

    eco = Mock()
    disease = Mock()

    eco.contact_rate_multiplier = {"house": 1.0}
    eco.disease.incubation_period = 5.0
    eco.num_infections_today = 0

    disease.infection_rate = 1.0

    household = Household(sample_house, sample_ages, size=3)
    household.agents[0].status = "infectious"
    household.evolve(eco, disease)

    assert mock_probability.call_count == 2
    assert household.agents[0].status == "infectious"
    assert household.agents[1].status == "exposed"
    assert household.agents[2].status == "exposed"
