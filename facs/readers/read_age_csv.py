import sys
import numpy as np
import pandas as pd

def read_age_csv(csv_name, header_name=""):
    df = pd.read_csv(csv_name)
    df.columns = map(str.lower, df.columns)
    if header_name not in df.columns:
        header_name = "United Kingdom"
    ages = df[header_name.lower()].to_numpy()
    return ages / np.sum(ages)
