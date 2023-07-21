"""Module to read disease parameters and create a Disease object."""

import yaml
from facs.base.disease import Disease


def read_disease_yml(ymlfile: str) -> Disease:
    """Read disease parameters from a YAML file and create a Disease object."""

    with open(ymlfile, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        print(data)

    disease = Disease(
        data["infection_rate"],
        data["incubation_period"],
        data["mild_recovery_period"],
        data["recovery_period"],
        data["mortality_period"],
        data["period_to_hospitalisation"],
        data["immunity_duration"],
    )
    disease.add_hospitalisation_chances(data["hospitalised"])
    disease.add_mortality_chances(data["mortality"])
    disease.add_mutations(data["mutations"])
    print(disease)
    return disease
