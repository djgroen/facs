"""Test the Household class in the base module."""

import random

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
    household = Household(sample_house, sample_ages)
    assert household.house == sample_house
    assert household.ages == sample_ages
    assert len(household.agents) == household.size


def test_get_infectious_count(sample_house, sample_ages):
    """Test get_infectious_count method in Household class."""
    household = Household(sample_house, sample_ages)
    # You may need to manipulate the agents' statuses here to simulate different scenarios
    assert isinstance(household.get_infectious_count(), int)


def test_is_infected(sample_house, sample_ages):
    """Test is_infected method in Household class."""
    household = Household(sample_house, sample_ages)
    # Manipulate the agents' statuses here to test different scenarios
    assert isinstance(household.is_infected(), bool)


def test_evolve(sample_house, sample_ages):
    """Test evolve method in Household class."""
    household = Household(sample_house, sample_ages)
    # Setup necessary mock or real objects for the 'e' and 'disease' parameters
    # Test evolve method behavior
    assert ...  # Assertions based on evolve method's expected behavior


# Additional tests as needed
