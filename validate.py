"""Validation script for the FACS model."""

import sys
import warnings
from datetime import datetime

import matplotlib
import pandas as pd

matplotlib.use("Pdf")

warnings.filterwarnings("ignore")


def load_output_data(out_dir):
    """Load the output data from the FACS model."""

    filename = f"{out_dir}/out.csv"
    facs_output = pd.read_csv(filename, sep=",", encoding="latin1")

    return facs_output


def load_admissions_data(out_dir):
    """Load the admissions data from the validation data."""

    filename = f"{out_dir}/covid_data/admissions.csv"
    val_adm_output = pd.read_csv(filename, sep=",", encoding="latin1")

    return val_adm_output


def validate():
    """Validate the FACS model."""

    d_sim = load_output_data(sys.argv[1])
    d_adm = load_admissions_data(sys.argv[1])
    start_date = datetime.strptime("1/3/2020", "%d/%m/%Y")

    # Validation data preprocessing.
    d_adm["date"] = pd.to_datetime(d_adm["date"], format="%d/%m/%Y")
    d_adm["days"] = (d_adm["date"] - start_date).dt.days

    d_adm.sort_values(by=["days"], inplace=True)

    validation_table = {"days": [], "admissions": [], "admissions sim": []}

    for _, row in d_adm.iterrows():
        day = int(row["days"])
        adm = int(row["admissions"])
        adm_sim = d_sim.loc[d_sim["#time"] == day]["num hospitalisations today"].values[
            0
        ]
        validation_table["days"].append(day)
        validation_table["admissions"].append(adm)
        validation_table["admissions sim"].append(adm_sim)

    # conversion from dict to DF.
    d_val = pd.DataFrame.from_dict(validation_table)

    # df extension
    d_val["cum admissions"] = d_val["admissions"].cumsum()
    d_val["cum admissions sim"] = d_val["admissions sim"].cumsum()
    d_val["admissions error"] = (
        d_val["cum admissions"] - d_val["cum admissions sim"]
    ).abs()

    print(f"input directory: {sys.argv[1]}")
    print("totals:")
    print(f"  cumulative admissions data: {d_val['cum admissions'].iloc[-1]}")
    print(f"  cumulative admissions sim: {d_val['cum admissions sim'].iloc[-1]}")
    mape = d_val["admissions error"].mean() / d_val["cum admissions"].mean()
    print(f"  MAPE: {mape:.2f}")


if __name__ == "__main__":
    validate()
