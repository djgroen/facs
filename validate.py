import pandas as pd
import matplotlib

matplotlib.use("Pdf")
import matplotlib.pyplot as plt
import numpy as np
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")


def load_output_data(out_dir):
    facs_output = pd.read_csv("%s/out.csv" % (out_dir), sep=",", encoding="latin1")

    return facs_output


def load_admissions_data(out_dir):
    val_adm_output = pd.read_csv(
        "%s/covid_data/admissions.csv" % (out_dir), sep=",", encoding="latin1"
    )

    return val_adm_output


if __name__ == "__main__":
    d_sim = load_output_data(sys.argv[1])
    d_adm = load_admissions_data(sys.argv[1])
    start_date = datetime.strptime("1/3/2020", "%d/%m/%Y")

    # Validation data preprocessing.
    d_adm["date"] = pd.to_datetime(d_adm["date"], format="%d/%m/%Y")
    d_adm["days"] = (d_adm["date"] - start_date).dt.days

    d_adm.sort_values(by=["days"], inplace=True)

    # print(d_adm['days'].max(),d_adm['days'].min())

    # print(d_sim["cum num hospitalisations today"],d_adm["days"],d_adm["admissions"], d_adm["admissions"].cumsum())

    # dict building
    validation_table = {"days": [], "admissions": [], "admissions sim": []}

    for index, row in d_adm.iterrows():
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

    print("input directory: {}".format(sys.argv[1]))
    print("totals:")
    print("  cumulative admissions data: {}".format(d_val["cum admissions"].iloc[-1]))
    print(
        "  cumulative admissions sim: {}".format(d_val["cum admissions sim"].iloc[-1])
    )
    print(
        "  MAPE: {}".format(
            d_val["admissions error"].mean() / d_val["cum admissions"].mean()
        )
    )

    # print(d_val['admissions error'].mean(), d_val['cum admissions'].mean(), d_val['admissions error'].mean() / d_val['cum admissions'].mean())
