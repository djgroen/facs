# FLACS: FLu And Coronavirus Simulator

## How to run the code
To run a simple simulation of a basic test dataset, type:
`python3 run.py --location=test --transition_scenario=extend-lockdown --transition_mode=1 --output_dir=.`

To run a simulation of the Borough of Brent, type:
`python3 run.py --location=brent --transition_scenario=extend-lockdown --transition_mode=1 --output_dir=.`

Outputs are written as CSV files in the output\_dir. E.g. for the test run you will get:
covid\_out\_infections.csv
test-extend-lockdown-62.csv

There is a hardcoded lockdown in run.py which is representative for the UK. This can be disabled by selecting the transition scenario "no-measures".

We also included a simple plotting script. This can be called e.g. as follows:
`python3 PlotSEIR.py test-extend-lockdown-62.csv test`
