# FACS: Flu And Coronavirus Simulator

![Code Tests](https://github.com/djgroen/facs/actions/workflows/pytest.yml/badge.svg)
[![GitHub Issues](https://img.shields.io/github/issues/djgroen/facs.svg)](https://github.com/djgroen/facs/issues)
[![GitHub last-commit](https://img.shields.io/github/last-commit/djgroen/facs.svg)](https://github.com/djgroen/facs/commits/master)

Full documentation can be found at: http://facs.readthedocs.io

## What is FACS?

FACS is an agent-based modeling code that simulates the spread of flu and coronaviruses in local regions. So far, it has been used to model the spread of infectious across various regions in Europe, including the United Kingdom, specifically Greater London, South-East, and North-West England; Lithuania’s region of Klaipėda; Romania’s city of Călărași; and Türkiye’s cities of Ankara and Istanbul.

## How FACS Works?

FACS operates by mapping agents to their natural geographical locations, simulating realistic movement and interactions. Each agent is assigned specific attributes, which influence their behavior, such as travel patterns and adherence to health guidelines set by authorities. Agents move between locations based on their needs, with some following health rules while others may not.

When agents gather in the same location, infections can spread through proximity to infected agents, allowing them to carry and transmit the infection to other locations as they travel. FACS progresses on a daily basis, updating agent locations and health states to simulate the spread of infection over time.

## FACS Supported Arguments

The current supported arguments for running FACS are listed below. These allow users to customize simulation parameters such as location, starting infections, disease configuration, and more:

- **--location**: Sets the location for the simulation (e.g., --location=test).
- **--measures_yml**: Specifies the YAML file containing intervention measures (e.g., --measures_yml=measures_uk).
- **--disease_yml**: Specifies the YAML configuration file for disease parameters (e.g., --disease_yml=disease_covid19 or --disease_yml=disease_measles).
- **--vaccinations_yml**: Specifies the YAML configuration file for vaccination parameters (e.g., - **--vaccinations_yml=vaccinations).
- **--output_dir**: Defines the directory where output files are saved (default: .).
- **--data_dir**: Directory for data files relevant to the simulation, such as COVID- and measles-related data (e.g., --data_dir=covid_data).
- **--starting_infections**: Initial number of infections at the start of the simulation (e.g., --starting_infections=1).
- **--household_size**: Average household size for the simulated population (e.g., --household_size=2.6).
- **--start_date**: Start date of the simulation in dd/mm/yyyy format (e.g., --start_date=1/3/2020).
- **--quicktest**: Enables a quick test mode if set to True, for faster run times with minimal processing (default: False).
- **--generic_outfile**: If enabled (True), produces a generic output file without location-specific data (default: False).
- **--dbg**: Enables debugging mode for additional output and information (default: False).
- **--simulation_period**: Duration of the simulation in days. Use -1 for an indefinite period (e.g., --simulation_period=30).
- **--office_size**: Specifies the maximum office size, impacting workplace infections (e.g., --office_size=2500).
- **--workspace**: Sets the average workspace area in square feet, which affects infection spread in office settings (e.g., --workspace=20).
- **--seed**: Sets a specific seed for random number generation, ensuring reproducible results (e.g., --seed=42).

### Example usage

```bash
python run.py --location=test --measures_yml=measures_uk --disease_yml=disease_covid19 --vaccinations_yml=vaccinations --output_dir=. --data_dir=covid_data --starting_infections=1 --start_date=1/3/2020 --simulation_period=-1 --household_size=2.6 --office_size=2500 --workspace=20 
```

This example sets up a simulation with 1 initial infections, running indefinitely, with data sourced from covid_data and using the disease_covid19.yml configuration file.

## Parallel Execution with MPI

FACS is parallelized and can take advantage of multiple processors to speed up simulations, especially useful for large-scale scenarios. To run FACS in parallel, use the mpirun command, which allows distribution of tasks across available processors.

**Requirements**: Ensure that MPI (Message Passing Interface) is installed on your system. Most systems use OpenMPI or MPICH for MPI support. Full description is provided in FACS [Read-the-Docs](http://facs.readthedocs.io).

### Example Usage: To run FACS on 4 processors, use the following command

```bash
mpirun -np 4 python run.py --location=test --measures_yml=measures_uk --disease_yml=disease_covid19 --vaccinations_yml=vaccinations --output_dir=. --data_dir=covid_data --starting_infections=1 --start_date=1/3/2020 --simulation_period=1
```

In this example, -np 4 specifies that FACS should run across 4 processors. Adjust the number of processors as needed, based on the resources available on your system.

### Benefits of Parallelization

Running FACS with MPI enables efficient handling of complex simulations, reducing execution time and allowing for scalability across different regions or larger populations. This parallelization capability is especially useful for simulations with high computational demands, such as modeling extensive population movement or disease spread across multiple locations.

## Available Locations and Customization

FACS includes over 20 pre-configured locations within the covid_data directory such as `harrow`, `hillingdon` and `brent`, allowing users to quickly set up simulations for various regions. If you’d like to experiment with these provided locations, simply specify the desired location using the --location argument (e.g., --location=location_name).

For users who wish to create custom locations, FACS supports user-defined locations. To create a new location, follow the guidelines provided in the documentation. This flexibility enables users to adapt FACS to specific geographic areas or custom scenarios beyond the predefined options.

## FACS Output

FACS generates two types of output files, providing detailed insights into the simulation:

### Individual Event Files:

These files contain information on individual infections, hospitalizations, recoveries, and deaths. Each file is generated in CSV format and named according to the event and processor rank:

- out_infections_rank.csv
- out_hospitalisations_rank.csv
- out_recoveries_rank.csv
- out_deaths_rank.csv

Each of these files includes time-stamped data on individual events, allowing for granular analysis of how the disease progresses and affects the population over time.

### Comprehensive Location Output

FACS also produces a full summary output for the entire simulation, saved in the format location-<measures>.csv. This file consolidates data across all individual events and provides an overview of the outcomes for the specified location and intervention measures.

These output files are invaluable for analyzing simulation results, tracking disease spread, and assessing the impact of different intervention strategies.

## Post-Processing and Analysis

After generating output files, FACS provides several scripts for post-processing and analyzing simulation results. These scripts enable users to visualize trends in infections, hospitalizations, recoveries, and deaths.

For instance, the PlotSEIR.py script creates an interactive SEIR (Susceptible-Exposed-Infectious-Recovered) plot, allowing users to analyze changes in disease states over time.

### Usage Example

```bash
python PlotSEIR.py test-measures_uk.csv test
```

This command generates an HTML file (test.html) that visualizes the data from test-measures_uk.csv.

### PlotSEIR.py Code Explanation

The PlotSEIR.py script reads a specified CSV file and generates a plot with the following elements:

- **New Cases**: Calculated as the daily change in the exposed and infectious populations.
- **Susceptible**: The number of individuals susceptible to infection.
- **Exposed**: The number of individuals exposed to the virus.
- **Infectious**: The number of infectious individuals actively spreading the virus.
- **Recovered**: The cumulative number of recovered individuals.
- **Dead**: The cumulative number of deaths.
  
Each of these elements is plotted over time using the plotly library, creating a detailed SEIR visualization.

#### Example Code (PlotSEIR.py)

```python
import sys
import pandas as pd
import plotly as py
import plotly.graph_objects as go

# Load data from the specified CSV file
df = pd.read_csv(sys.argv[1], delimiter=",")

# Calculate daily new cases
df["new cases"] = df["exposed"].diff(1) + df["infectious"].diff(1)

# Initialize the plot figure
fig = go.Figure()

# Add traces for each SEIR component
fig.add_trace(go.Scatter(x=df["#time"], y=df["susceptible"], mode="lines+markers", name="susceptible", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=df["#time"], y=df["exposed"], mode="lines+markers", name="exposed", line=dict(color="purple")))
fig.add_trace(go.Bar(x=df["#time"], y=df["new cases"], name="change in # affected"))
fig.add_trace(go.Scatter(x=df["#time"], y=df["infectious"], mode="lines+markers", name="infectious", line=dict(color="red")))
fig.add_trace(go.Scatter(x=df["#time"], y=df["recovered"], mode="lines+markers", name="recovered", line=dict(color="green")))
fig.add_trace(go.Scatter(x=df["#time"], y=df["dead"], mode="lines+markers", name="dead", line=dict(color="black")))

# Save plot as an HTML file
py.offline.plot(fig, filename=f"{sys.argv[2]}.html")
```

The output of this script is an HTML file that opens in a web browser, showing an interactive plot with line and bar charts for each SEIR component, enabling users to explore infection trends and other key metrics over time.

This post-processing tool and similar scripts make FACS data analysis more accessible, offering insights into the spread and control of infectious diseases.

## Quick Tests

You can run quick tests by using the -q flag. This increases the house ratio to 100 (default is 2), which reduces distribution accuracy but speeds up the simulation significantly.

### Example command

```bash
python run.py -q --location=brent --output_dir=.
```

The results are saved to the specified output_dir on your local machine.

## Running Large-Scale Simulations

For users interested in running large-scale simulations locally or on remote systems, we recommend exploring [FabSim3](https://github.com/djgroen/FabSim3) and [FabCovid19](https://github.com/djgroen/FabCovid19). These tools extend FACS’s capabilities, making it easier to manage complex simulations across multiple machines, automate workflows, and efficiently handle high-performance computing environments.

**Note**: If you experience any issues, please raise a GitHub issue so we can assist you.
