import numpy as np
import pandas as pd

from facs.readers.read_age_csv import read_age_csv


def test_read_age_csv_real_data():
    # Assuming the file exists in the specified directory and has a consistent format
    csv_name = 'covid_data/age_distribution.csv'
    header_name = 'United Kingdom'  # Adjust this based on the actual header in the CSV
    
    # Load the CSV manually to calculate expected outputs
    df = pd.read_csv(csv_name)
    df.columns = map(str.lower, df.columns)  # Ensure headers are correctly formatted
    assert header_name.lower() in df.columns, f"Header {header_name} must be in the CSV"

    # Get the actual output from the function
    result = read_age_csv(csv_name, header_name)
    
    # Calculate expected output directly
    expected_output = df[header_name.lower()].to_numpy() / np.sum(df[header_name.lower()].to_numpy())
    
    # Check if the outputs match
    assert np.allclose(result, expected_output), "The function's output should match the calculated expected output"
