# FACS: Flu And Coronavirus Simulator

[![Build Status](https://travis-ci.com/djgroen/facs.svg?branch=master)](https://travis-ci.com/djgroen/facs)
[![GitHub Issues](https://img.shields.io/github/issues/djgroen/facs.svg)](https://github.com/djgroen/facs/issues)
[![GitHub last-commit](https://img.shields.io/github/last-commit/djgroen/facs.svg)](https://github.com/djgroen/facs/commits/master)


Full documentation can be found at: http://facs.readthedocs.io

## How to run the code
To run a simple simulation of a basic test dataset, type:
`python3 run.py --location=test --output_dir=.`

To run it in parallel, type (for four core runs):
`mpirun -np 4 python3 run.py --location=test --output_dir=.`

To do a run of custom length (with -t flag), and with a generically named out.csv output file, type:
`mpirun -np 1 python3 run.py -t=10 -g --location=test --output_dir=.`

To run a simulation of the Borough of Brent, type:
`python3 run.py --location=brent --output_dir=.`

To run a simulation of Brunel University London, type:
`python3 run_campus.py --location=brunel --output_dir=.`

Outputs are written as CSV files in the output\_dir. E.g. for the test run you will get:
covid\_out\_infections.csv
test-extend-lockdown-62.csv

There is a hardcoded lockdown in run.py which is representative for the UK. This can be disabled by selecting the transition scenario "no-measures".

We also included a simple plotting script. This can be called e.g. as follows:
`python3 PlotSEIR.py test-extend-lockdown-62.csv test`

## Advanced usage

### Running with a specific data directory
Flacs can be run with a different input data directory as follows:
`python3 run.py --location=brent --output_dir=. --data_dir=/home/derek/covid19-postprocess/facs_input_private`

### Performing quick tests
Quick tests can be triggered with the '-q' flag. This sets the house ratio to 100 (default is 2), which means that households will be less well distributed.
However, as a number of calculations are performed on the house level (not the household level), this setting speeds up the code by up to an order of magnitude.
`python3 run.py -q --location=brent --output_dir=.`

## Submitting jobs to the GridPP via HTCondor
Facs directory contains four additional files: 
`script_grid.sh (bash script for job submission automation)`
`run_grid.py (python script equivalent to run.py for job submission)`
`joblist_grid.txt (list of jobs with facs arguments for job queuing)`
`job_grid.submit (contains the configuration for facs simulations)`

After initiating the python environment, the pyinstaller package can be used to create an executable from 'run_grid.py'. 
`pyinstaller run_grid.py --onefile`

There are currently 18 locations (jobs) in the 'joblist_grid.txt' file. (optional) 
The jobs are submitted with the command: 
`condor_submit job_grid.submit`

The results are transferred back to the local machine and placed in 'output_dir'.

